import boto3
import os
from dotenv import load_dotenv
import json
import fitz  # PyMuPDF
import re

# Load environment variables
load_dotenv('passbook.env')

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")


class PassbookExtractor:
    def __init__(self):
        self.textract = boto3.client(
            "textract",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )

    def extract_passbook_data(self, user_id):
        document_key = f"{user_id}/sample-passbook.pdf"

        try:
            # Download PDF from S3
            response = self.s3.get_object(Bucket=S3_BUCKET_NAME, Key=document_key)
            pdf_bytes = response['Body'].read()

            # Convert PDF to images
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            all_key_value_pairs = []
            full_text = ""  # Store all text for IFSC regex search

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap()
                img_data = pix.tobytes("png")

                # Textract analyze_document
                response = self.textract.analyze_document(
                    Document={'Bytes': img_data},
                    FeatureTypes=['FORMS']
                )

                for block in response['Blocks']:
                    if block['BlockType'] == 'KEY_VALUE_SET' and 'KEY' in block.get('EntityTypes', []):
                        key_text = self._get_text_from_block(block, response['Blocks'])
                        value_block = self._find_value_block(block, response['Blocks'])
                        value_text = self._get_text_from_block(value_block, response['Blocks']) if value_block else ""

                        if key_text.strip():
                            all_key_value_pairs.append({
                                'Key': key_text.strip(),
                                'Value': value_text.strip()
                            })
                            full_text += " " + key_text + " " + value_text
                    elif block['BlockType'] == 'LINE':
                        # Add all lines to full_text to search for IFSC
                        full_text += " " + block.get('Text', '')

            doc.close()

            # Use regex to find IFSC if missing
            ifsc_match = re.search(r'\b[A-Z]{4}0[A-Z0-9]{6}\b', full_text)
            if ifsc_match:
                ifsc_code = ifsc_match.group(0)
                if not any("IFSC" in kv['Key'].upper() for kv in all_key_value_pairs):
                    all_key_value_pairs.append({
                        'Key': 'IFSC',
                        'Value': ifsc_code
                    })

            # Save JSON only
            json_file = f"{user_id}_passbook_extracted.json"
            with open(json_file, "w") as f:
                json.dump(all_key_value_pairs, f, indent=2)

            # Upload JSON back to S3
            self.s3.upload_file(json_file, S3_BUCKET_NAME, f"out/{user_id}/{json_file}")

            return {
                "status": "success",
                "extracted_pairs_count": len(all_key_value_pairs),
                "json_file": json_file,
                "data": all_key_value_pairs
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _get_text_from_block(self, block, all_blocks):
        if not block or 'Relationships' not in block:
            return ""
        text = ""
        for rel in block['Relationships']:
            if rel['Type'] == 'CHILD':
                for child_id in rel['Ids']:
                    child_block = next((b for b in all_blocks if b['Id'] == child_id), None)
                    if child_block and child_block['BlockType'] == 'WORD':
                        text += child_block['Text'] + " "
        return text.strip()

    def _find_value_block(self, key_block, all_blocks):
        if 'Relationships' not in key_block:
            return None
        for rel in key_block['Relationships']:
            if rel['Type'] == 'VALUE':
                value_id = rel['Ids'][0]
                return next((b for b in all_blocks if b['Id'] == value_id), None)
        return None


def extract_passbook(user_id):
    extractor = PassbookExtractor()
    return extractor.extract_passbook_data(user_id)


if __name__ == "__main__":
    user_id = input("Enter user ID: ")
    result = extract_passbook(user_id)
    print(json.dumps(result, indent=2))
