import json
import boto3
import re
import csv
import uuid
from io import StringIO
from urllib.parse import unquote_plus
from datetime import datetime

# Initialize AWS clients
textract = boto3.client('textract')
s3 = boto3.client('s3')

def lambda_handler(event, context):
    """Lambda function triggered by S3 upload for Aadhar extraction"""
    
    try:
        # Get S3 event details
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = unquote_plus(event['Records'][0]['s3']['object']['key'])
        
        # Check if file matches criteria for Aadhar
        if not (key.startswith('aadhar') and (key.endswith('.pdf') or key.endswith('.jpg') or key.endswith('.png'))):
            return {
                'statusCode': 200,
                'body': json.dumps('File does not match Aadhar criteria - skipping')
            }
        
        print(f"Processing Aadhar file: {key} from bucket: {bucket}")
        
        # Extract text using Textract
        lines = extract_text_from_s3(bucket, key)
        
        # Extract Aadhar details
        details = extract_aadhar_details(lines, key)
        
        # Save as CSV
        csv_key = save_to_csv(bucket, key, details)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Aadhar extraction completed successfully',
                'source_file': key,
                'output_file': csv_key,
                'extracted_data': details
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error processing file: {str(e)}')
        }

def extract_text_from_s3(bucket, key):
    """Extract text from S3 document using Textract"""
    response = textract.detect_document_text(
        Document={'S3Object': {'Bucket': bucket, 'Name': key}}
    )
    
    lines = []
    for item in response['Blocks']:
        if item['BlockType'] == 'LINE':
            lines.append(item['Text'])
    
    return lines

def extract_aadhar_details(lines, source_file):
    """Extract Aadhar card details from text lines"""
    
    # Generate unique user ID
    user_id = str(uuid.uuid4())
    
    # Aadhar number - 12 digits, can be with or without spaces/dashes
    aadhar_number = None
    for line in lines:
        # Look for 12-digit number pattern
        match = re.search(r'\b(\d{4}[\s-]?\d{4}[\s-]?\d{4})\b', line)
        if match:
            # Clean the number (remove spaces and dashes)
            aadhar_number = re.sub(r'[\s-]', '', match.group(1))
            if len(aadhar_number) == 12:
                break
    
    # Name - usually appears after specific keywords or in specific positions
    name = None
    for i, line in enumerate(lines):
        # Skip lines that contain Aadhar number or government text
        if aadhar_number and aadhar_number in line.replace(' ', '').replace('-', ''):
            continue
        if any(keyword in line.lower() for keyword in ['government', 'india', 'unique', 'identification']):
            continue
            
        # Look for name patterns - typically appears as a standalone line with proper case
        if re.match(r'^[A-Z][a-z]+(?: [A-Z][a-z]+)*$', line.strip()) and len(line.strip()) > 3:
            name = line.strip()
            break
    
    # Date of Birth - various formats
    dob = None
    for line in lines:
        # Look for date patterns
        date_patterns = [
            r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b',  # DD/MM/YYYY or DD-MM-YYYY
            r'\b(\d{4})[/-](\d{1,2})[/-](\d{1,2})\b',  # YYYY/MM/DD or YYYY-MM-DD
            r'\b(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})\b'  # DD Mon YYYY
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                if len(match.groups()) == 3:
                    if pattern == date_patterns[2]:  # Month name format
                        day, month_name, year = match.groups()
                        month_map = {'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04', 
                                   'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
                                   'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'}
                        month = month_map.get(month_name.lower()[:3], '01')
                        dob = f"{day.zfill(2)}-{month}-{year}"
                    else:
                        parts = match.groups()
                        if pattern == date_patterns[0]:  # DD/MM/YYYY
                            dob = f"{parts[0].zfill(2)}-{parts[1].zfill(2)}-{parts[2]}"
                        else:  # YYYY/MM/DD
                            dob = f"{parts[2].zfill(2)}-{parts[1].zfill(2)}-{parts[0]}"
                    break
        if dob:
            break
    
    # Address - usually a longer line with address components
    address = None
    for line in lines:
        # Skip lines with Aadhar number, name, or government text
        if aadhar_number and aadhar_number in line.replace(' ', '').replace('-', ''):
            continue
        if name and name.lower() in line.lower():
            continue
        if any(keyword in line.lower() for keyword in ['government', 'india', 'unique', 'identification']):
            continue
            
        # Look for address-like patterns (longer lines with address keywords)
        if len(line.strip()) > 20 and any(keyword in line.lower() for keyword in 
                                        ['s/o', 'd/o', 'w/o', 'village', 'district', 'state', 'pin', 'house', 'street']):
            address = line.strip()
            break
    
    # Gender - look for Male/Female
    gender = None
    for line in lines:
        if re.search(r'\b(male|female)\b', line, re.IGNORECASE):
            match = re.search(r'\b(male|female)\b', line, re.IGNORECASE)
            gender = match.group(1).title()
            break
    
    # Current timestamp
    processed_date = datetime.now().strftime("%d-%m-%Y %H:%M")
    
    return {
        'user_id': user_id,
        'aadhar_number': aadhar_number,
        'name': name,
        'dob': dob,
        'address': address,
        'gender': gender,
        'processed_date': processed_date,
        'source_file': source_file
    }

def save_to_csv(bucket, source_key, details):
    """Save extracted details to CSV in S3"""
    # Create CSV content
    csv_buffer = StringIO()
    writer = csv.writer(csv_buffer)
    
    # Write header matching your expected format
    writer.writerow(['user_id', 'aadhar_number', 'name', 'dob', 'address', 'gender', 'processed_date', 'source_file'])
    
    # Write data
    writer.writerow([
        details.get('user_id', ''),
        details.get('aadhar_number', ''),
        details.get('name', ''),
        details.get('dob', ''),
        details.get('address', ''),
        details.get('gender', ''),
        details.get('processed_date', ''),
        details.get('source_file', '')
    ])
    
    # Generate CSV filename
    csv_key = source_key.replace('.pdf', '_extracted.csv').replace('.jpg', '_extracted.csv').replace('.png', '_extracted.csv')
    
    # Upload CSV to S3
    s3.put_object(
        Bucket=bucket,
        Key=csv_key,
        Body=csv_buffer.getvalue(),
        ContentType='text/csv'
    )
    
    print(f"CSV saved as: {csv_key}")
    return csv_key