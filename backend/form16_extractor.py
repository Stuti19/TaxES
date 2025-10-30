import boto3
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
                
                # Use Textract on the image with both FORMS and TABLES
                response = self.textract.analyze_document(
                    Document={'Bytes': img_data},
                    FeatureTypes=['FORMS', 'TABLES']
                )
                
                # Extract key-value pairs from FORMS
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
                
                # Extract additional key-value pairs from table cells
                table_kvp = self._extract_kvp_from_tables(response['Blocks'])
                all_key_value_pairs.extend(table_kvp)
            
            doc.close()
            
            # Save to JSON
            json_filename = "form16_extracted.json"
            with open(json_filename, 'w') as f:
                json.dump(all_key_value_pairs, f, indent=2)
            
            return {
                'status': 'success',
                'extracted_pairs_count': len(all_key_value_pairs),
                'json_file': json_filename,
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
    
    def _extract_kvp_from_tables(self, blocks):
        kvp_pairs = []
        table_blocks = [block for block in blocks if block['BlockType'] == 'TABLE']
        
        for table_block in table_blocks:
            table_data = []
            if 'Relationships' in table_block:
                for relationship in table_block['Relationships']:
                    if relationship['Type'] == 'CHILD':
                        for cell_id in relationship['Ids']:
                            cell_block = next((b for b in blocks if b['Id'] == cell_id), None)
                            if cell_block and cell_block['BlockType'] == 'CELL':
                                row_index = cell_block.get('RowIndex', 1) - 1
                                col_index = cell_block.get('ColumnIndex', 1) - 1
                                cell_text = self._get_text_from_block(cell_block, blocks)
                                
                                while len(table_data) <= row_index:
                                    table_data.append([])
                                while len(table_data[row_index]) <= col_index:
                                    table_data[row_index].append('')
                                
                                table_data[row_index][col_index] = cell_text.strip()
            
            # Extract key-value pairs from table rows
            for row in table_data:
                if len(row) >= 2 and row[0] and row[1]:
                    key = str(row[0]).strip()
                    value = str(row[1]).strip()
                    
                    # Skip headers and non-meaningful pairs
                    if (key and value and 
                        not key.lower() in ['details', 'description', 'rs.', 'amount', 'gross amount', 'deductible amount'] and
                        not value.lower() in ['rs.', 'amount', 'description']):
                        
                        kvp_pairs.append({
                            'Key': key,
                            'Value': value,
                            'Confidence': 85.0
                        })
                        
                # Handle 3+ column tables (key, description, amount)
                if len(row) >= 3 and row[0] and row[2]:
                    key = str(row[0]).strip()
                    description = str(row[1]).strip() if row[1] else ''
                    value = str(row[2]).strip()
                    
                    if (key and value and description and
                        not key.lower() in ['details', 'rs.', 'amount', 'gross amount'] and
                        not value.lower() in ['rs.', 'amount', 'description'] and
                        '10(' in description or '16(' in description or '80' in description):
                        
                        combined_key = f"{key} {description}".strip()
                        kvp_pairs.append({
                            'Key': combined_key,
                            'Value': value,
                            'Confidence': 85.0
                        })
        
        return kvp_pairs

def extract_form16(user_id):
    extractor = Form16Extractor()
    return extractor.extract_form16_data(user_id)

if __name__ == "__main__":
    user_id = input("Enter user ID: ")
    result = extract_form16(user_id)
    print(json.dumps(result, indent=2))