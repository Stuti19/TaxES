import json
import re

class Form16Parser:
    def __init__(self):
        self.required_fields = {
            'assessment_year': ['assessment year'],
            'pan': ['pan of the employee/specified senior citizen', 'pan of the employee'],
            'employee_address': ['name and address of the employee/specified senior citizen'],
            'gross_salary': ['gross salary', 'total'],
            'salary_section_17_1': ['17(1)'],
            'prerequisites_section_17_2': ['17(2)'],
            'profits_section_17_3': ['17(3)'],
            'total_exemption_section_10': ['total amount of exemption claimed under section 10'],
            'standard_deduction_16_ia': ['standard deduction under section 16(ia)'],
            'entertainment_allowance_16_ii': ['entertainment allowance under section 16(ii)'],
            'tax_on_employment_16_iii': ['tax on employment under section 16(iii)'],
            'income_chargeable_salaries': ['income chargeable under the head "salaries"'],
            'gross_total_income': ['gross total income'],
            'deduction_80C': ['80c'],
            'deduction_80CCC': ['80ccc'],
            'deduction_80CCD1': ['80ccd (1)', '80ccd(1)'],
            'deduction_80CCD1B': ['80ccd (1b)', '80ccd(1b)'],
            'deduction_80CCD2': ['80ccd (2)', '80ccd(2)'],
            'deduction_80D': ['80d'],
            'deduction_80E': ['80e'],
            'deduction_80G': ['80g'],
            'deduction_80TTA': ['80tta'],
            'deduction_80C_total': ['total deduction under section 80c, 80ccc and 80ccd(1)'],
            'tax_on_total_income': ['tax on total income'],
            'rebate_87A': ['87a'],
            'surcharge': ['surcharge'],
            'health_education_cess': ['health and education cess'],
            'relief_section_89': ['relief under section 89'],
            'tax_payable': ['net tax payable', 'tax payable']
        }

    def parse_form16_data(self, extracted_data):
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
                    if field_name in ['gross_salary', 'salary_section_17_1', 'prerequisites_section_17_2', 
                                    'profits_section_17_3', 'total_exemption_section_10', 'standard_deduction_16_ia',
                                    'entertainment_allowance_16_ii', 'tax_on_employment_16_iii', 'income_chargeable_salaries',
                                    'gross_total_income', 'deduction_80C', 'deduction_80CCC',
                                    'deduction_80CCD1', 'deduction_80CCD1B', 'deduction_80CCD2', 'deduction_80D',
                                    'deduction_80E', 'deduction_80G', 'deduction_80TTA', 'deduction_80C_total',
                                    'tax_on_total_income', 'rebate_87A', 'surcharge', 'health_education_cess',
                                    'relief_section_89', 'tax_payable']:
                        parsed_result[field_name] = self._parse_amount(value)
                    else:
                        parsed_result[field_name] = value
                    break
        
        # Process tables for additional data extraction
        table_data = self._extract_from_tables(tables)
        parsed_result.update(table_data)
        
        # Calculate gross salary from 17(1) + 17(2) + 17(3)
        section_17_1 = parsed_result.get('salary_section_17_1', 0) or 0
        section_17_2 = parsed_result.get('prerequisites_section_17_2', 0) or 0
        section_17_3 = parsed_result.get('profits_section_17_3', 0) or 0
        
        if isinstance(section_17_1, str):
            section_17_1 = float(section_17_1) if section_17_1 else 0
        if isinstance(section_17_2, str):
            section_17_2 = float(section_17_2) if section_17_2 else 0
        if isinstance(section_17_3, str):
            section_17_3 = float(section_17_3) if section_17_3 else 0
            
        parsed_result['gross_salary'] = section_17_1 + section_17_2 + section_17_3
        
        # Get proper assessment year (not masked)
        for item in key_value_pairs:
            key = item['Key'].lower().strip()
            value = item['Value'].strip()
            if 'assessment year' in key and not any(x in value for x in ['x', '*', '=', '<']):
                parsed_result['assessment_year'] = value
                break
        
        # Specific check for gross_total_income
        for item in key_value_pairs:
            key = item['Key'].lower().strip()
            value = item['Value'].strip()
            confidence = item['Confidence']
            
            if 'gross total income' in key and value and confidence >= 40:
                parsed_result['gross_total_income'] = self._parse_amount(value)
                break
        
        # Specific checks for deduction fields
        deduction_patterns = {
            'deduction_80C': ['80c'],
            'deduction_80CCC': ['80ccc'],
            'deduction_80CCD1': ['80ccd(1)', '80ccd (1)'],
            'deduction_80CCD1B': ['80ccd(1b)', '80ccd (1b)'],
            'deduction_80CCD2': ['80ccd(2)', '80ccd (2)'],
            'deduction_80D': ['80d'],
            'deduction_80E': ['80e'],
            'deduction_80G': ['80g'],
            'deduction_80TTA': ['80tta'],
            'deduction_80C_total': ['total deduction under section 80c']
        }
        
        for field_name, patterns in deduction_patterns.items():
            if not parsed_result.get(field_name):
                for item in key_value_pairs:
                    key = item['Key'].lower().strip()
                    value = item['Value'].strip()
                    confidence = item['Confidence']
                    
                    if any(pattern in key for pattern in patterns) and value and confidence >= 40:
                        parsed_result[field_name] = self._parse_amount(value)
                        break
        
        # Specific check for tax_on_total_income
        if not parsed_result.get('tax_on_total_income'):
            for item in key_value_pairs:
                key = item['Key'].lower().strip()
                value = item['Value'].strip()
                confidence = item['Confidence']
                
                if 'tax on total income' in key and value and confidence >= 40:
                    parsed_result['tax_on_total_income'] = self._parse_amount(value)
                    break
        
        # Calculate total_exemption_section_10 from individual section 10 exemptions
        if not parsed_result.get('total_exemption_section_10'):
            section_10_total = 0
            section_10_patterns = ['10(5)', '10 (5)', '10(10)', '10 (10)', '10(10a)', '10 (10a)', '10(10aa)', '10 (10aa)', '10(13a)', '10 (13a)']
            
            for item in key_value_pairs:
                key = item['Key'].lower().strip()
                value = item['Value'].strip()
                
                if any(pattern in key for pattern in section_10_patterns) and value:
                    try:
                        amount = self._parse_amount(value)
                        section_10_total += amount
                    except:
                        continue
            
            if section_10_total > 0:
                parsed_result['total_exemption_section_10'] = section_10_total

        return parsed_result

    def _parse_amount(self, value):
        amount_match = re.search(r'[\d,]+\.?\d*', value.replace(',', ''))
        return float(amount_match.group()) if amount_match else 0.0
    
    def _extract_from_tables(self, tables):
        table_extracted = {}
        
        for table in tables:
            table_data = table.get('table_data', [])
            if not table_data:
                continue
                
            # Look for salary breakdown tables, deduction tables, etc.
            for row_idx, row in enumerate(table_data):
                if len(row) >= 2:
                    key = str(row[0]).lower().strip() if row[0] else ''
                    value = str(row[1]).strip() if row[1] else ''
                    
                    if not key or not value:
                        continue
                    
                    # Match table data to required fields
                    for field_name, keywords in self.required_fields.items():
                        if any(keyword in key for keyword in keywords):
                            if field_name in ['gross_salary', 'salary_section_17_1', 'prerequisites_section_17_2', 
                                            'profits_section_17_3', 'total_exemption_section_10', 'standard_deduction_16_ia',
                                            'entertainment_allowance_16_ii', 'tax_on_employment_16_iii', 'income_chargeable_salaries',
                                            'gross_total_income', 'deduction_80C', 'deduction_80CCC',
                                            'deduction_80CCD1', 'deduction_80CCD1B', 'deduction_80CCD2', 'deduction_80D',
                                            'deduction_80E', 'deduction_80G', 'deduction_80TTA', 'deduction_80C_total',
                                            'tax_on_total_income', 'rebate_87A', 'surcharge', 'health_education_cess',
                                            'relief_section_89', 'tax_payable']:
                                table_extracted[field_name] = self._parse_amount(value)
                            else:
                                table_extracted[field_name] = value
                            break
        
        return table_extracted

    def save_parsed_data(self, parsed_data, user_id):
        filename = f"{user_id}_form16_parsed.json"
        with open(filename, 'w') as f:
            json.dump(parsed_data, f, indent=2)
        return filename

def parse_form16(user_id, extracted_data_file=None):
    parser = Form16Parser()
    
    if not extracted_data_file:
        extracted_data_file = f"{user_id}_form16_extracted.json"
    
    try:
        parsed_data = parser.parse_form16_data(extracted_data_file)
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
    result = parse_form16(user_id)
    print(json.dumps(result, indent=2))