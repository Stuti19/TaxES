import json
import re

class AadharParser:
    def __init__(self):
        self.required_fields = {
            'name': ['name'],
            'dob': ['dob', 'date of birth', 'birth'],
            'address': ['address'],
            'gender': ['gender', 'sex'],
            'aadharNumber': ['aadhar', 'aadhaar', 'uid', 'enrollment']
        }

    def parse_aadhar_data(self, extracted_data):
        if isinstance(extracted_data, str):
            with open(extracted_data, 'r') as f:
                data = json.load(f)
        else:
            data = extracted_data

        parsed_result = {field: '' for field in self.required_fields.keys()}
        
        if isinstance(data, dict) and 'data' in data:
            key_value_pairs = data['data']
        else:
            key_value_pairs = data

        # Skip initial keyword matching for DOB as it causes issues
        for item in key_value_pairs:
            key = item['Key'].lower().strip()
            value = item['Value'].strip()
            confidence = item['Confidence']

            if not value or confidence < 40:
                continue

            for field_name, keywords in self.required_fields.items():
                if field_name == 'dob':  # Skip DOB in initial matching
                    continue
                if any(keyword.lower() in key.lower() for keyword in keywords):
                    if field_name == 'aadharNumber':
                        parsed_result[field_name] = self._parse_aadhar_number(value)
                    else:
                        parsed_result[field_name] = value
                    break

        # Extract Aadhar number - exclude VID numbers
        if not parsed_result['aadharNumber']:
            for item in key_value_pairs:
                key = item['Key'].lower().strip()
                value = item['Value'].strip()
                # Skip if key contains 'vid'
                if 'vid' in key:
                    continue
                aadhar_match = re.search(r'\b\d{4}\s?\d{4}\s?\d{4}\b', value)
                if aadhar_match:
                    parsed_result['aadharNumber'] = aadhar_match.group().replace(' ', '')
                    break
        
        # Extract gender from MALE/FEMALE keywords
        if not parsed_result['gender']:
            for item in key_value_pairs:
                value = item['Value'].strip().upper()
                if 'MALE' in value or 'FEMALE' in value:
                    if 'FEMALE' in value:
                        parsed_result['gender'] = 'FEMALE'
                    elif 'MALE' in value:
                        parsed_result['gender'] = 'MALE'
                    break
        
        # Extract DOB - skip entries with key "Date"
        if not parsed_result['dob']:
            for item in key_value_pairs:
                key = item['Key'].strip()
                value = item['Value'].strip()
                
                # Skip entries with key "Date"
                if key.lower() == 'date':
                    continue
                    
                date_match = re.search(r'\b\d{2}/\d{2}/\d{4}\b', value)
                if date_match:
                    parsed_result['dob'] = date_match.group()
                    break
        
        # Extract name - look for name in key or value
        if not parsed_result['name']:
            for item in key_value_pairs:
                key = item['Key'].strip()
                value = item['Value'].strip()
                
                # Check if key contains a name (like "Anjali JOH PR / DOB")
                name_in_key = re.search(r'^([A-Za-z]+)\s', key)
                if name_in_key and len(name_in_key.group(1)) > 2:
                    parsed_result['name'] = name_in_key.group(1)
                    break
                
                # Fallback: check value for name patterns
                if (len(value.split()) >= 2 and 
                    not re.search(r'\d', value) and 
                    'government' not in value.lower() and
                    not any(x in value.lower() for x in ['male', 'female', 'address', 'dob', 'vid', 'aadhar', 'india', 'authority']) and
                    len(value) > 3):
                    parsed_result['name'] = value
                    break
        
        # Extract address - combine all address-like entries
        if not parsed_result['address']:
            address_parts = []
            
            for item in key_value_pairs:
                value = item['Value'].strip()
                
                # Look for address patterns (contains numbers or location indicators)
                if (len(value) > 10 and 
                    (re.search(r'\d', value) or 
                     any(x in value.lower() for x in ['road', 'street', 'nagar', 'colony', 'delhi', 'mumbai', 'bangalore', 'pin', 'block', 'sector', 'area', 'north', 'south', 'east', 'west']))):
                    
                    # Skip if contains father's/husband's name indicators
                    if any(x in value.upper() for x in ['S/O', 'D/O', 'W/O']):
                        # Extract only address part after S/O, D/O, W/O
                        parts = re.split(r'[,;]', value)
                        for part in parts:
                            part = part.strip()
                            if (not any(x in part.upper() for x in ['S/O', 'D/O', 'W/O']) and 
                                len(part) > 5 and
                                (re.search(r'\d', part) or 
                                 any(x in part.lower() for x in ['road', 'street', 'nagar', 'colony', 'delhi', 'mumbai', 'bangalore', 'block', 'sector', 'area']))):
                                address_parts.append(part)
                    else:
                        # Skip government text and other non-address content
                        if (not any(x in value.lower() for x in ['government', 'india', 'authority', 'identification', 'male', 'female']) and
                            not re.search(r'\b\d{4}\s?\d{4}\s?\d{4}\b', value)):  # Skip aadhar numbers
                            address_parts.append(value)
            
            if address_parts:
                parsed_result['address'] = ' '.join(address_parts)

        return parsed_result

    def _parse_aadhar_number(self, value):
        aadhar_match = re.search(r'\b\d{4}\s?\d{4}\s?\d{4}\b', value)
        return aadhar_match.group().replace(' ', '') if aadhar_match else value



    def _parse_date(self, value):
        date_patterns = [
            r'\d{2}/\d{2}/\d{4}',
            r'\d{2}-\d{2}-\d{4}',
            r'\d{4}/\d{2}/\d{2}',
            r'\d{4}-\d{2}-\d{2}'
        ]
        for pattern in date_patterns:
            date_match = re.search(pattern, value)
            if date_match:
                return date_match.group()
        return value

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
    user_id = input("Enter user ID: ")
    result = parse_aadhar(user_id)
    print(json.dumps(result, indent=2))