import boto3
import pandas as pd
import os
from dotenv import load_dotenv
import json
import fitz  # PyMuPDF

load_dotenv()

class Form16Extractor:
    def __init__(self):
        self.textract = boto3.client(
            'textract',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')
        )
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')
        )
        self.bucket_name = os.getenv('S3_BUCKET_NAME')

    def extract_form16_data(self, user_id):
        document_key = f"{user_id}/form16.pdf"
        
        try:
            # Download PDF from S3
            response = self.s3.get_object(Bucket=self.bucket_name, Key=document_key)
            pdf_bytes = response['Body'].read()
            
            # Convert PDF to images using PyMuPDF
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            all_key_value_pairs = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap()
                img_data = pix.tobytes("png")
                
                # Use Textract on the image
                response = self.textract.analyze_document(
                    Document={'Bytes': img_data},
                    FeatureTypes=['FORMS']
                )
                
                # Extract key-value pairs
                for block in response['Blocks']:
                    if block['BlockType'] == 'KEY_VALUE_SET' and 'KEY' in block.get('EntityTypes', []):
                        key_text = self._get_text_from_block(block, response['Blocks'])
                        value_block = self._find_value_block(block, response['Blocks'])
                        value_text = self._get_text_from_block(value_block, response['Blocks']) if value_block else ""
                        confidence = block.get('Confidence', 0)
                        
                        if key_text.strip():
                            all_key_value_pairs.append({
                                'Key': key_text.strip(),
                                'Value': value_text.strip(),
                                'Confidence': round(confidence, 2)
                            })
            
            doc.close()
            
            # Save to CSV
            csv_filename = f"{user_id}_form16_extracted.csv"
            df = pd.DataFrame(all_key_value_pairs)
            df.to_csv(csv_filename, index=False)
            
            return {
                'status': 'success',
                'extracted_pairs_count': len(all_key_value_pairs),
                'csv_file': csv_filename,
                'data': all_key_value_pairs
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def _get_text_from_block(self, block, all_blocks):
        if not block or 'Relationships' not in block:
            return ""
        
        text = ""
        for relationship in block['Relationships']:
            if relationship['Type'] == 'CHILD':
                for child_id in relationship['Ids']:
                    child_block = next((b for b in all_blocks if b['Id'] == child_id), None)
                    if child_block and child_block['BlockType'] == 'WORD':
                        text += child_block['Text'] + " "
        return text.strip()

    def _find_value_block(self, key_block, all_blocks):
        if 'Relationships' not in key_block:
            return None
        
        for relationship in key_block['Relationships']:
            if relationship['Type'] == 'VALUE':
                value_id = relationship['Ids'][0]
                return next((b for b in all_blocks if b['Id'] == value_id), None)
        return None

def extract_form16(user_id):
    extractor = Form16Extractor()
    return extractor.extract_form16_data(user_id)

if __name__ == "__main__":
    user_id = input("Enter user ID: ")
    result = extract_form16(user_id)
    print(json.dumps(result, indent=2))