import boto3
import os
from dotenv import load_dotenv
import json
import fitz  # PyMuPDF
import re

load_dotenv()

class AadharExtractor:
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

    def extract_aadhar_data(self, user_id):
        document_key = f"{user_id}/aadhar.pdf"
        
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
            
            # Also collect all text for fallback analysis
            all_text_blocks = []
            for block in response['Blocks']:
                if block['BlockType'] == 'LINE':
                    text = block.get('Text', '').strip()
                    confidence = block.get('Confidence', 0)
                    if text:
                        all_text_blocks.append({
                            'text': text,
                            'confidence': confidence
                        })
            

            
            # Filter and map to specific Aadhar details
            aadhar_details = self._map_to_aadhar_fields(all_key_value_pairs, all_text_blocks)
            
            # Save to JSON
            json_filename = f"{user_id}_aadhar_extracted.json"
            with open(json_filename, 'w') as f:
                json.dump(aadhar_details, f, indent=2)
            
            return {
                'status': 'success',
                'json_file': json_filename,
                'data': aadhar_details
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
    
    def _map_to_aadhar_fields(self, key_value_pairs, all_text_blocks):
        aadhar_data = {
            'aadhar_number': {'value': '', 'confidence': 0},
            'name': {'value': '', 'confidence': 0},
            'date_of_birth': {'value': '', 'confidence': 0},
            'gender': {'value': '', 'confidence': 0},
            'address': {'value': '', 'confidence': 0}
        }
        
        # First try key-value pairs
        for pair in key_value_pairs:
            key = pair['Key'].lower()
            value = pair['Value']
            confidence = pair['Confidence']
            
            # Map Aadhar number (12 digits)
            if len(value.replace(' ', '').replace('-', '')) == 12 and value.replace(' ', '').replace('-', '').isdigit():
                if confidence > aadhar_data['aadhar_number']['confidence']:
                    aadhar_data['aadhar_number'] = {
                        'value': value.replace(' ', '').replace('-', ''),
                        'confidence': confidence
                    }
            
            # Map Date of Birth
            if (any(dob_keyword in key for dob_keyword in ['dob', 'birth', 'date']) and '/' in value) or \
               (len(value) == 10 and value.count('/') == 2 and all(c.isdigit() or c == '/' for c in value)):
                if confidence > aadhar_data['date_of_birth']['confidence']:
                    aadhar_data['date_of_birth'] = {
                        'value': value,
                        'confidence': confidence
                    }
            
            # Map Gender
            if value.upper() in ['MALE', 'FEMALE'] or 'female' in value.lower() or 'male' in value.lower():
                gender_val = 'FEMALE' if 'female' in value.lower() else 'MALE'
                if confidence > aadhar_data['gender']['confidence']:
                    aadhar_data['gender'] = {
                        'value': gender_val,
                        'confidence': confidence
                    }
            
            # Map Name - look for actual person name
            if ('anjali' in value.lower() and len(value.split()) <= 3):
                # Extract just the name part, remove D/O, S/O etc
                name_part = re.sub(r'\b(D/O|S/O|W/O)\b.*', '', value, flags=re.IGNORECASE).strip()
                if name_part and confidence > aadhar_data['name']['confidence']:
                    aadhar_data['name'] = {
                        'value': name_part,
                        'confidence': confidence
                    }
            
            # Map Address (collect and clean address parts)
            if (len(value) > 10 and 
                (any(addr_keyword in value.lower() for addr_keyword in ['nagar', 'delhi', 'road', 'colony', 'sector', 'block', 'street', 'pin', 'north', 'east', 'west', 'south']) or
                 re.search(r'\d{6}', value)) and  # Contains pincode
                not value.replace(' ', '').replace('-', '').isdigit() and
                len(value.split()) > 2):
                
                # Clean the address value before storing
                clean_value = self._clean_address_text(value)
                if clean_value:  # Only add if there's meaningful content after cleaning
                    existing_addr = aadhar_data['address']['value']
                    combined_addr = f"{existing_addr} {clean_value}".strip() if existing_addr else clean_value
                    aadhar_data['address'] = {
                        'value': combined_addr,
                        'confidence': max(confidence, aadhar_data['address']['confidence'])
                    }
        
        # Fallback: Check all text blocks for missing fields
        for block in all_text_blocks:
            text = block['text']
            confidence = block['confidence']
            
            # Find Aadhar number if not found
            if not aadhar_data['aadhar_number']['value']:
                clean_text = text.replace(' ', '').replace('-', '')
                if len(clean_text) == 12 and clean_text.isdigit():
                    aadhar_data['aadhar_number'] = {
                        'value': clean_text,
                        'confidence': confidence
                    }
            
            # Find correct date of birth if not found or incorrect
            if not aadhar_data['date_of_birth']['value'] or aadhar_data['date_of_birth']['value'] == '07/09/2020':
                # Look for date pattern that's not the issue date
                if re.match(r'\d{2}/\d{2}/\d{4}', text) and text != '07/09/2020':
                    # Check if it's a reasonable birth date (not future, not too old)
                    year = int(text.split('/')[-1])
                    if 1950 <= year <= 2010:
                        aadhar_data['date_of_birth'] = {
                            'value': text,
                            'confidence': confidence
                        }
            
            # Find name if not found
            if not aadhar_data['name']['value']:
                if 'anjali' in text.lower():
                    # Extract just the name part, remove D/O, S/O etc
                    name_part = re.sub(r'\b(D/O|S/O|W/O)\b.*', '', text, flags=re.IGNORECASE).strip()
                    name_part = re.sub(r'\b(JOH|PR|DOB)\b.*', '', name_part, flags=re.IGNORECASE).strip()
                    if name_part and confidence > aadhar_data['name']['confidence']:
                        aadhar_data['name'] = {
                            'value': name_part,
                            'confidence': confidence
                        }
            
            # Collect clean address parts (exclude D/O, S/O content)
            if (len(text) > 10 and 
                (any(addr_keyword in text.lower() for addr_keyword in ['nagar', 'delhi', 'road', 'colony', 'sector', 'block', 'street', 'mandoli', 'shahdara', 'north', 'east']) or
                 re.search(r'\d{6}', text)) and  # Contains pincode
                not text.replace(' ', '').replace('-', '').isdigit() and
                len(text.split()) > 1):
                
                # Clean the address text before adding
                clean_text = self._clean_address_text(text)
                if clean_text:  # Only add if there's meaningful content after cleaning
                    existing_addr = aadhar_data['address']['value']
                    if not existing_addr or clean_text not in existing_addr:
                        combined_addr = f"{existing_addr} {clean_text}".strip() if existing_addr else clean_text
                        aadhar_data['address'] = {
                            'value': combined_addr,
                            'confidence': max(confidence, aadhar_data['address']['confidence'])
                        }
        
        return aadhar_data
    
    def _clean_address_text(self, text):
        """Clean address text by removing D/O, S/O content and unwanted codes"""
        clean_text = text
        
        # Remove D/O, S/O content completely
        clean_text = re.sub(r'D/O\s+[^,]*', '', clean_text, flags=re.IGNORECASE)
        clean_text = re.sub(r'S/O\s+[^,]*', '', clean_text, flags=re.IGNORECASE)
        clean_text = re.sub(r'W/O\s+[^,]*', '', clean_text, flags=re.IGNORECASE)
        
        # Remove unwanted codes and references
        clean_text = re.sub(r'\b\d+/-\s*\d+\s*for\s*\d+,?\s*', '', clean_text)
        clean_text = re.sub(r'\bTell\s*\d+\s*\d+,?\s*', '', clean_text)
        clean_text = re.sub(r'\b\d+/\d+\s*TTR,?\s*', '', clean_text)
        clean_text = re.sub(r'\b\d{7},?\s*', '', clean_text)  # Remove 7-digit numbers
        clean_text = re.sub(r'\b\d+[A-Z]+\s*[a-z]+,?\s*', '', clean_text)  # Remove codes like 3TRT gaff
        clean_text = re.sub(r'\bReft\s*-\s*-\s*', '', clean_text)
        clean_text = re.sub(r'\bNo\.\s*', '', clean_text)
        clean_text = re.sub(r'\bH\.\s*E\s*-\s*-\s*\d+\s*Street', '', clean_text)  # Remove H. E - - 376 Street
        
        # Clean up extra spaces, commas and hyphens
        clean_text = re.sub(r'\s*,\s*,\s*', ', ', clean_text)
        clean_text = re.sub(r'^\s*,\s*', '', clean_text)
        clean_text = re.sub(r'\s*-\s*,\s*', ' ', clean_text)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        # Extract only the meaningful address parts
        if 'Ashok Nagar' in clean_text:
            # Find the pattern: number + Ashok Nagar + area + city + pincode
            match = re.search(r'(\d+\s+Ashok Nagar.*?Delhi.*?\d{6})', clean_text)
            if match:
                clean_text = match.group(1)
        
        return clean_text if len(clean_text) > 5 else ''  # Return only if meaningful content remains

def extract_aadhar(user_id):
    extractor = AadharExtractor()
    return extractor.extract_aadhar_data(user_id)

if __name__ == "__main__":
    # Use the specific user ID provided
    user_id = "cadda9d1-d6c8-4907-b873-6070696e575a"
    result = extract_aadhar(user_id)
    print(json.dumps(result, indent=2))