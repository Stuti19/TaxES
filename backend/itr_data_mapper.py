import pandas as pd
import openpyxl
from openpyxl import load_workbook
import os
from datetime import datetime
from aadhar_extractor import extract_aadhar_details, extract_text_from_s3_pdf
from passbook_extractor import extract_passbook_details
import boto3
from dotenv import load_dotenv
import win32com.client
import re

load_dotenv()

# Indian States List
INDIAN_STATES = [
    'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa', 'Gujarat', 
    'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 
    'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 
    'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura', 'Uttar Pradesh', 
    'Uttarakhand', 'West Bengal', 'Delhi', 'Jammu and Kashmir', 'Ladakh', 'Puducherry'
]

class ITRDataMapper:
    def __init__(self, template_path):
        self.template_path = template_path
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')
        )
        
    def extract_user_data(self, user_id, bucket_name):
        """Extract data from both Aadhaar and passbook for a user"""
        extracted_data = {}
        
        # Extract Aadhaar data
        aadhar_key = f"{user_id}/aadhar.pdf"
        try:
            lines = extract_text_from_s3_pdf(bucket_name, aadhar_key)
            if lines:
                aadhar_details = extract_aadhar_details(lines)
                extracted_data.update(aadhar_details)
                print(f"✓ Aadhaar data extracted for {user_id}")
        except Exception as e:
            print(f"✗ Error extracting Aadhaar for {user_id}: {str(e)}")
        
        # Extract Passbook data
        passbook_key = f"{user_id}/passbook.pdf"
        try:
            lines = extract_text_from_s3_pdf(bucket_name, passbook_key)
            if lines:
                passbook_details = extract_passbook_details(lines)
                extracted_data.update(passbook_details)
                print(f"✓ Passbook data extracted for {user_id}")
        except Exception as e:
            print(f"✗ Error extracting passbook for {user_id}: {str(e)}")
            
        return extracted_data
    
    def split_name(self, full_name):
        """Split full name into first, middle, last"""
        if not full_name:
            return '', '', ''
        
        parts = full_name.strip().split()
        if len(parts) == 1:
            return parts[0], '', ''
        elif len(parts) == 2:
            return parts[0], '', parts[1]
        else:
            return parts[0], ' '.join(parts[1:-1]), parts[-1]
    
    def extract_state_from_address(self, address):
        """Extract state from address"""
        if not address:
            return ''
        
        address_lower = address.lower()
        for state in INDIAN_STATES:
            if state.lower() in address_lower:
                return state
        return ''
    
    def extract_pincode_from_address(self, address):
        """Extract 6-digit pincode from address"""
        if not address:
            return ''
        
        pincode_match = re.search(r'\b\d{6}\b', address)
        return pincode_match.group() if pincode_match else ''
    
    def map_data_to_template(self, extracted_data, output_path):
        """Map extracted data to ITR template Excel file"""
        try:
            workbook = load_workbook(self.template_path)
            worksheet = workbook.active
            
            # Handle name splitting
            name = extracted_data.get('name')
            if name:
                first, middle, last = self.split_name(name)
                worksheet['E7'] = first
                worksheet['O7'] = middle
                worksheet['Y7'] = last
                print(f"✓ Name split: {first} | {middle} | {last}")
            else:
                worksheet['E7'] = worksheet['O7'] = worksheet['Y7'] = ''
            
            # Handle address parsing
            address = extracted_data.get('address', '')
            state = self.extract_state_from_address(address)
            pincode = self.extract_pincode_from_address(address)
            
            # Map all fields including Aadhaar number
            worksheet['AN7'] = ''  # PAN
            worksheet['AN8'] = extracted_data.get('aadhar_number', '')  # Aadhaar number
            worksheet['E11'] = ''  # Flat/Door/Block
            worksheet['AN11'] = extracted_data.get('dob', '')
            worksheet['E13'] = ''  # Road/Street
            worksheet['W13'] = ''  # Area/Locality
            worksheet['AN13'] = '' # Town/City
            worksheet['W15'] = 'India'  # Country
            worksheet['E15'] = state
            worksheet['AA15'] = pincode
            worksheet['B20'] = extracted_data.get('accountNumber', '')
            worksheet['B22'] = extracted_data.get('bankName', '')
            worksheet['B24'] = extracted_data.get('IFSC_Code', '')
            
            print(f"✓ Mapped: Aadhaar={extracted_data.get('aadhar_number')}, DOB={extracted_data.get('dob')}, State={state}, Pincode={pincode}")
            
            workbook.save(output_path)
            print(f"✓ Excel filled: {output_path}")
            return True
            
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            return False
    
    def convert_to_pdf(self, excel_path):
        """Convert Excel to PDF"""
        try:
            pdf_path = excel_path.replace('.xlsx', '.pdf')
            
            # Try multiple approaches
            try:
                import win32com.client as win32
                excel_app = win32.gencache.EnsureDispatch('Excel.Application')
                excel_app.Visible = False
                excel_app.DisplayAlerts = False
                
                workbook = excel_app.Workbooks.Open(os.path.abspath(excel_path))
                workbook.ExportAsFixedFormat(0, os.path.abspath(pdf_path))
                workbook.Close(SaveChanges=False)
                excel_app.Quit()
                
                os.remove(excel_path)
                print(f"✓ PDF created: {pdf_path}")
                return pdf_path
                
            except:
                # Fallback: just return Excel file
                print(f"✗ PDF conversion failed, keeping Excel file")
                return excel_path
                
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            return excel_path
    
    def process_user_itr(self, user_id, bucket_name, output_dir="filled_templates"):
        """Complete process: extract data and fill ITR template for a user"""
        os.makedirs(output_dir, exist_ok=True)
        
        extracted_data = self.extract_user_data(user_id, bucket_name)
        if not extracted_data:
            return None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        excel_path = os.path.join(output_dir, f"ITR_{user_id}_{timestamp}.xlsx")
        
        if self.map_data_to_template(extracted_data, excel_path):
            pdf_path = self.convert_to_pdf(excel_path)
            return pdf_path
        return None
    
    def process_all_users(self, bucket_name):
        """Process ITR templates for all users in the bucket"""
        try:
            response = self.s3.list_objects_v2(Bucket=bucket_name, Delimiter='/')
            user_folders = []
            if 'CommonPrefixes' in response:
                for prefix in response['CommonPrefixes']:
                    folder = prefix['Prefix'].rstrip('/')
                    if folder != 'extracted_data':  # Skip extracted_data folder
                        user_folders.append(folder)
            
            print(f"Found {len(user_folders)} users: {user_folders}")
            
            processed_files = []
            for user_id in user_folders:
                print(f"\n--- Processing ITR for user: {user_id} ---")
                output_path = self.process_user_itr(user_id, bucket_name)
                if output_path:
                    processed_files.append(output_path)
            
            print(f"\n✓ Successfully processed {len(processed_files)} ITR templates")
            return processed_files
            
        except Exception as e:
            print(f"✗ Error processing users: {str(e)}")
            return []

def update_field_mapping(new_mapping):
    """Update the field mapping configuration"""
    global ITR_FIELD_MAPPING
    ITR_FIELD_MAPPING.update(new_mapping)
    print("✓ Field mapping updated")

if __name__ == "__main__":
    template_path = "itr_temp.xlsx"
    bucket_name = os.getenv('S3_BUCKET_NAME')
    
    if not os.path.exists(template_path):
        print(f"✗ Template file not found: {template_path}")
    else:
        mapper = ITRDataMapper(template_path)
        processed_files = mapper.process_all_users(bucket_name)
        print(f"\n✓ Processed {len(processed_files)} PDF files")