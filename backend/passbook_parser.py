import json
import re

class PassbookParser:
    def __init__(self):
        self.required_fields = {
            'name': ['account holder', 'name', 'customer name'],
            'accountNumber': ['account number', 'account no', 'a/c no'],
            'bankName': ['bank', 'bank name'],
            'IFSC_Code': ['ifsc', 'ifsc code']
        }
        
        # Bank names to identify from text
        self.bank_names = [
            'State Bank of India', 'SBI', 'Punjab National Bank', 'PNB',
            'Bank of Baroda', 'Canara Bank', 'Bank of India', 'Union Bank of India',
            'Bank of Maharashtra', 'Indian Bank', 'Central Bank of India',
            'Indian Overseas Bank', 'UCO Bank', 'Punjab & Sind Bank',
            'HDFC Bank', 'ICICI Bank', 'Kotak Mahindra Bank', 'Axis Bank',
            'IndusInd Bank', 'Federal Bank', 'Yes Bank'
        ]
        
        # IFSC prefix to bank name mapping
        self.ifsc_to_bank = {
            'SBIN': 'State Bank of India',
            'PUNB': 'Punjab National Bank',
            'BARB': 'Bank of Baroda',
            'CNRB': 'Canara Bank',
            'BKID': 'Bank of India',
            'UBIN': 'Union Bank of India',
            'MAHB': 'Bank of Maharashtra',
            'IDIB': 'Indian Bank',
            'CBIN': 'Central Bank of India',
            'IOBA': 'Indian Overseas Bank',
            'UCBA': 'UCO Bank',
            'PSIB': 'Punjab & Sind Bank',
            'HDFC': 'HDFC Bank',
            'ICIC': 'ICICI Bank',
            'KKBK': 'Kotak Mahindra Bank',
            'UTIB': 'Axis Bank',
            'INDB': 'IndusInd Bank',
            'FDRL': 'Federal Bank',
            'YESB': 'Yes Bank'
        }

    def parse_passbook_data(self, extracted_data):
        if isinstance(extracted_data, str):
            with open(extracted_data, 'r') as f:
                data = json.load(f)
        else:
            data = extracted_data

        parsed_result = {field: '' for field in self.required_fields.keys()}
        
        # Handle new data structure with key_value_pairs and tables
        if isinstance(data, dict) and 'key_value_pairs' in data:
            key_value_pairs = data['key_value_pairs']
            tables = data.get('tables', [])
        else:
            # Backward compatibility with old format
            key_value_pairs = data
            tables = []

        # Process key-value pairs
        for item in key_value_pairs:
            key = item['Key'].lower().strip()
            value = item['Value'].strip()
            confidence = item['Confidence']

            if not value or confidence < 40:
                continue

            for field_name, keywords in self.required_fields.items():
                if any(keyword.lower() in key.lower() for keyword in keywords):
                    if field_name == 'accountNumber':
                        parsed_result[field_name] = self._parse_account_number(value)
                    elif field_name == 'IFSC_Code':
                        parsed_result[field_name] = self._parse_ifsc(value)
                    else:
                        parsed_result[field_name] = value
                    break
        
        # Process tables for additional data extraction
        table_data = self._extract_from_tables(tables)
        parsed_result.update(table_data)
        
        # Extract account number from any field containing account number pattern
        if not parsed_result['accountNumber']:
            for item in key_value_pairs:
                value = item['Value'].strip()
                account_match = re.search(r'\b\d{9,18}\b', value)
                if account_match and len(account_match.group()) >= 9:
                    parsed_result['accountNumber'] = account_match.group()
                    break

        # Extract IFSC code pattern
        if not parsed_result['IFSC_Code']:
            for item in key_value_pairs:
                value = item['Value'].strip()
                ifsc_match = re.search(r'\b[A-Z]{4}0[A-Z0-9]{6}\b', value)
                if ifsc_match:
                    parsed_result['IFSC_Code'] = ifsc_match.group()
                    break
        
        # First priority: determine bank name from IFSC code
        if parsed_result['IFSC_Code']:
            ifsc_prefix = parsed_result['IFSC_Code'][:4]
            if ifsc_prefix in self.ifsc_to_bank:
                parsed_result['bankName'] = self.ifsc_to_bank[ifsc_prefix]
        
        # Fallback: extract bank name from text only if IFSC didn't match
        if not parsed_result['bankName']:
            for item in key_value_pairs:
                value = item['Value'].strip()
                
                # Check if value contains any bank name
                for bank_name in self.bank_names:
                    if bank_name.lower() in value.lower():
                        parsed_result['bankName'] = bank_name
                        break
                if parsed_result['bankName']:
                    break

        return parsed_result

    def _parse_account_number(self, value):
        account_match = re.search(r'\b\d{9,18}\b', value)
        return account_match.group() if account_match else value

    def _parse_ifsc(self, value):
        ifsc_match = re.search(r'\b[A-Z]{4}0[A-Z0-9]{6}\b', value)
        return ifsc_match.group() if ifsc_match else value
    
    def _extract_from_tables(self, tables):
        table_extracted = {}
        
        for table in tables:
            table_data = table.get('table_data', [])
            if not table_data:
                continue
                
            # Look for passbook details in tables
            for row_idx, row in enumerate(table_data):
                if len(row) >= 2:
                    key = str(row[0]).lower().strip() if row[0] else ''
                    value = str(row[1]).strip()
                    
                    # Match against required fields
                    for field_name, keywords in self.required_fields.items():
                        if any(keyword.lower() in key for keyword in keywords) and value:
                            if field_name == 'accountNumber':
                                table_extracted[field_name] = self._parse_account_number(value)
                            elif field_name == 'IFSC_Code':
                                table_extracted[field_name] = self._parse_ifsc(value)
                            else:
                                table_extracted[field_name] = value
                            break
                    
                    # Check for bank name in table values
                    if not table_extracted.get('bankName') and value:
                        for bank_name in self.bank_names:
                            if bank_name.lower() in value.lower():
                                table_extracted['bankName'] = bank_name
                                break
        
        return table_extracted

    def save_parsed_data(self, parsed_data, user_id):
        filename = "passbook_parsed.json"
        with open(filename, 'w') as f:
            json.dump(parsed_data, f, indent=2)
        return filename

def parse_passbook(user_id, extracted_data_file=None):
    parser = PassbookParser()
    
    if not extracted_data_file:
        extracted_data_file = "passbook_extracted.json"
    
    try:
        parsed_data = parser.parse_passbook_data(extracted_data_file)
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
    result = parse_passbook(user_id)
    print(json.dumps(result, indent=2))