import json
import re

class AadharParser:
    def __init__(self):
        self.required_fields = {
            'aadhar_number': ['aadhar', 'aadhaar', 'uid'],
            'name': ['name'],
            'date_of_birth': ['dob', 'date of birth', 'birth'],
            'gender': ['gender', 'sex'],
            'address': ['address'],
            'father_name': ['father', 'f/o', 'fo'],
            'mobile': ['mobile', 'phone'],
            'email': ['email'],
            'vid': ['vid'],
            'pin_code': ['pin', 'pincode']
        }

    def parse_aadhar_data(self, extracted_data):
        if isinstance(extracted_data, str):
            with open(extracted_data, 'r') as f:
                data = json.load(f)
        else:
            data = extracted_data

        parsed_result = {field: '' for field in self.required_fields.keys()}
        
        # Handle extracted data structure
        if isinstance(data, dict):
            # Check if it's the direct structure from aadhar_extractor
            if 'aadhar_number' in data and isinstance(data['aadhar_number'], dict):
                # Direct structure with value/confidence pairs
                for field, field_data in data.items():
                    if field in parsed_result and isinstance(field_data, dict) and field_data.get('value'):
                        parsed_result[field] = field_data['value']
            elif 'data' in data:
                # Nested structure
                aadhar_data = data['data']
                for field, field_data in aadhar_data.items():
                    if field in parsed_result and field_data.get('value'):
                        parsed_result[field] = field_data['value']
        elif isinstance(data, list):
            # Old structure - list of key-value pairs
            for item in data:
                key = item['Key'].lower().strip()
                value = item['Value'].strip()
                confidence = item['Confidence']

                if not value or confidence < 40:
                    continue

                for field_name, keywords in self.required_fields.items():
                    if any(keyword.lower() in key.lower() for keyword in keywords):
                        if field_name == 'aadhar_number':
                            parsed_result[field_name] = self._parse_aadhar_number(value)
                        elif field_name == 'date_of_birth':
                            parsed_result[field_name] = self._parse_date(value)
                        elif field_name == 'gender':
                            parsed_result[field_name] = self._parse_gender(value)
                        elif field_name == 'pin_code':
                            parsed_result[field_name] = self._parse_pin_code(value)
                        else:
                            parsed_result[field_name] = value
                        break

        # Clean and validate data
        parsed_result = self._clean_and_validate(parsed_result)
        
        # Extract pincode from address if not already extracted
        if not parsed_result.get('pin_code') and parsed_result.get('address'):
            pin_match = re.search(r'\b\d{6}\b', parsed_result['address'])
            if pin_match:
                parsed_result['pin_code'] = pin_match.group()
        
        # Final address cleanup - ensure proper format
        if parsed_result.get('address'):
            addr = parsed_result['address']
            # Clean up any remaining issues
            addr = re.sub(r'\s+', ' ', addr).strip()
            parsed_result['address'] = addr
        
        return parsed_result

    def _parse_aadhar_number(self, value):
        # Extract 12-digit Aadhar number
        aadhar_match = re.search(r'\b\d{12}\b', value.replace(' ', '').replace('-', ''))
        return aadhar_match.group() if aadhar_match else value

    def _parse_date(self, value):
        # Standardize date format and validate
        date_match = re.search(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b', value)
        if date_match:
            date_str = date_match.group()
            # Check if it's a reasonable birth date
            year = int(date_str.split('/')[-1]) if '/' in date_str else int(date_str.split('-')[-1])
            if 1950 <= year <= 2010:  # Reasonable birth year range
                return date_str
        return value

    def _parse_gender(self, value):
        # Standardize gender
        if 'female' in value.lower():
            return 'FEMALE'
        elif 'male' in value.lower():
            return 'MALE'
        return value.upper()

    def _parse_pin_code(self, value):
        # Extract 6-digit PIN code from address
        pin_match = re.search(r'\b\d{6}\b', value)
        return pin_match.group() if pin_match else ''

    def _clean_and_validate(self, data):
        # Clean up the parsed data
        cleaned_data = {}
        
        for field, value in data.items():
            if isinstance(value, str):
                value = value.strip()
            
            # Validate Aadhar number
            if field == 'aadhar_number' and value:
                if len(value.replace(' ', '').replace('-', '')) == 12 and value.replace(' ', '').replace('-', '').isdigit():
                    cleaned_data[field] = value.replace(' ', '').replace('-', '')
                else:
                    cleaned_data[field] = ''
            
            # Validate date of birth
            elif field == 'date_of_birth' and value:
                if re.match(r'\d{1,2}[/-]\d{1,2}[/-]\d{4}', value):
                    # Additional validation for reasonable birth year
                    year = int(value.split('/')[-1]) if '/' in value else int(value.split('-')[-1])
                    if 1950 <= year <= 2010:
                        cleaned_data[field] = value
                    else:
                        cleaned_data[field] = ''
                else:
                    cleaned_data[field] = ''
            
            # Validate gender
            elif field == 'gender' and value:
                if value.upper() in ['MALE', 'FEMALE']:
                    cleaned_data[field] = value.upper()
                else:
                    cleaned_data[field] = ''
            
            # Clean name
            elif field == 'name' and value:
                # Remove common prefixes, D/O, S/O references and clean
                name = re.sub(r'\b(mr|mrs|ms|dr|prof)\.?\s*', '', value, flags=re.IGNORECASE)
                name = re.sub(r'\b(D/O|S/O|W/O)\b.*', '', name, flags=re.IGNORECASE)
                name = re.sub(r'\b(JOH|PR|DOB)\b.*', '', name, flags=re.IGNORECASE)
                cleaned_data[field] = name.strip().upper()
            
            # Handle address - should already be clean from extractor
            elif field == 'address' and value:
                # Just clean up spacing and remove trailing dash with pincode
                clean_addr = value
                clean_addr = re.sub(r'\s*-\s*\d{6}$', '', clean_addr)  # Remove trailing - pincode
                clean_addr = re.sub(r'\s+', ' ', clean_addr).strip()
                cleaned_data[field] = clean_addr
            
            # Extract pincode from address
            elif field == 'pin_code':
                if not value and 'address' in data:
                    # Extract from address field
                    address_value = data['address'] if isinstance(data['address'], str) else data['address'].get('value', '')
                    pin_match = re.search(r'\b\d{6}\b', address_value)
                    cleaned_data[field] = pin_match.group() if pin_match else ''
                else:
                    cleaned_data[field] = value
            
            else:
                cleaned_data[field] = value
        
        return cleaned_data

    def save_parsed_data(self, parsed_data, user_id):
        filename = f"{user_id}_aadhar_parsed.json"
        with open(filename, 'w') as f:
            json.dump(parsed_data, f, indent=2)
        return filename

def parse_aadhar(user_id, extracted_data_file=None):
    parser = AadharParser()
    
    if not extracted_data_file:
        extracted_data_file = f"{user_id}_aadhar_extracted.json"
    
    try:
        parsed_data = parser.parse_aadhar_data(extracted_data_file)
        output_file = parser.save_parsed_data(parsed_data, user_id)
        
        return {
            'status': 'success',
            'parsed_data': parsed_data,
            'output_file': output_file
        }
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

if __name__ == "__main__":
    # Use the specific user ID
    user_id = "cadda9d1-d6c8-4907-b873-6070696e575a"
    result = parse_aadhar(user_id)
    print(json.dumps(result, indent=2))