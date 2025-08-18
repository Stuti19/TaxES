import boto3
import re
import csv
import os
from datetime import datetime
from dotenv import load_dotenv
from botocore.exceptions import ClientError

load_dotenv()

textract = boto3.client(
    'textract',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

ALL_BANKS = [
    'State Bank of India', 'SBI',
    'Bank of India', 'BOI',
    'Bank of Baroda', 'BOB',
    'Punjab National Bank', 'PNB',
    'Central Bank of India',
    'Canara Bank',
    'Union Bank of India',
    'Indian Bank',
    'Axis Bank',
    'HDFC Bank',
    'ICICI Bank',
    'IDBI Bank',
    'Kotak Mahindra Bank', 'Kotak Bank',
    'Yes Bank',
    'IndusInd Bank',
    'UCO Bank',
    'Indian Overseas Bank'
]

def extract_text_from_s3_pdf(bucket, key):
    """Extract text from PDF using Textract"""
    try:
        response = textract.detect_document_text(
            Document={'S3Object': {'Bucket': bucket, 'Name': key}}
        )
        lines = []
        for item in response['Blocks']:
            if item['BlockType'] == 'LINE':
                line = item['Text'].strip()
                if line:
                    lines.append(line)
        return lines
    except Exception as e:
        print(f"Error extracting text from {key}: {str(e)}")
        return []

def extract_passbook_details(lines):
    details = {
        "accountNumber": "",
        "bankName": "",
        "IFSC_Code": ""
    }

    acc_number = ""
    
    # 1. First try explicit labeled account numbers only (account no, a/c no, acc no, etc.)
    acc_label_patterns = [
        r'(?i)account\s*(no\.?|number|num)?\s*[:\-]?\s*([0-9]{7,18})',
        r'(?i)a/c\s*no\.?\s*[:\-]?\s*([0-9]{7,18})',
        r'(?i)acc\s*no\.?\s*[:\-]?\s*([0-9]{7,18})',
        r'(?i)account\s*[:\-]?\s*([0-9]{7,18})'
    ]

    for line in lines:
        for pat in acc_label_patterns:
            match = re.search(pat, line)
            if match:
                acc_number = match.group(match.lastindex)
                # Extra filter: avoid CIF or Nom Reg labels near the number in line
                if re.search(r'cif|nom reg', line, re.IGNORECASE):
                    continue  # skip if CIF or Nom Reg label present
                break
        if acc_number:
            break
    
    # 2. If still not found, fallback to numeric sequences excluding CIF/Nom Reg
    if not acc_number:
        candidates = []
        joined_text = " ".join(lines)
        for m in re.finditer(r'\b[0-9]{9,14}\b', joined_text):
            start, end = m.start(), m.end()
            snippet = joined_text[max(0, start-20):min(len(joined_text), end+20)].lower()
            if any(x in snippet for x in ['cif', 'nom reg', 'nomination']):
                continue
            if m.group() and not m.group().startswith("0000"):
                candidates.append(m.group())
        if candidates:
            acc_number = max(candidates, key=len)

    details['accountNumber'] = acc_number

    # --- Bank Name ---
    bank_name = ""
    for line in lines:
        for bank in ALL_BANKS:
            if bank.lower() in line.lower():
                bank_name = bank
                break
        if bank_name:
            break
    if not bank_name:
        for line in lines:
            if 'bank' in line.lower():
                bank_name = line.strip()
                break
    details['bankName'] = bank_name

    # --- IFSC Code ---
    ifsc_code = ""
    for line in lines:
        match = re.search(r'IFSC\s*[:\-]?\s*([A-Z]{4}0[A-Z0-9]{6})', line)
        if match:
            ifsc_code = match.group(1)
            break
    if not ifsc_code:
        matches = re.findall(r'\b[A-Z]{4}0[A-Z0-9]{6}\b', ' '.join(lines))
        if matches:
            ifsc_code = matches[0]
    details['IFSC_Code'] = ifsc_code

    return details

def get_all_user_folders(bucket_name):
    try:
        response = s3.list_objects_v2(Bucket=bucket_name, Delimiter='/')
        folders = []
        if "CommonPrefixes" in response:
            for prefix in response['CommonPrefixes']:
                folders.append(prefix['Prefix'].rstrip('/'))
        return folders
    except Exception as e:
        print(f"Error listing folders: {str(e)}")
        return []

def safe_csv_writer(filename, headers, rows):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row in rows:
            writer.writerow(row)

def process_all_passbook_documents():
    bucket_name = os.getenv('S3_BUCKET_NAME')
    if not bucket_name:
        print("Error: S3_BUCKET_NAME not found in environment variables")
        return

    print(f"Processing passbook documents from bucket: {bucket_name}")
    user_folders = get_all_user_folders(bucket_name)
    print(f"Found {len(user_folders)} user folders: {user_folders}")

    csv_data = []
    csv_headers = ['user_id', 'accountNumber', 'bankName', 'IFSC_Code', 'processed_date', 'source_file']

    for user_id in user_folders:
        passbook_key = f"{user_id}/passbook.pdf"
        try:
            s3.head_object(Bucket=bucket_name, Key=passbook_key)
            print(f"Processing passbook for user: {user_id}")
            lines = extract_text_from_s3_pdf(bucket_name, passbook_key)
            if lines:
                details = extract_passbook_details(lines)
                csv_row = [
                    user_id,
                    details.get('accountNumber', ''),
                    details.get('bankName', ''),
                    details.get('IFSC_Code', ''),
                    datetime.now().strftime('%d-%m-%Y %H:%M'),
                    passbook_key
                ]
                csv_data.append(csv_row)
                print(f"✓ Extracted details for {user_id}: {details}")
            else:
                print(f"✗ No text extracted for {user_id}")
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                print(f"✗ No passbook.pdf found for user: {user_id}")
            else:
                print(f"✗ Error processing {user_id}: {str(e)}")
        except Exception as e:
            print(f"✗ Error processing {user_id}: {str(e)}")

    csv_filename = f"passbook_extracted_details_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    safe_csv_writer(csv_filename, csv_headers, csv_data)

    print(f"\n✓ CSV file created: {csv_filename}")
    print(f"✓ Processed {len(csv_data)} passbook documents")

    try:
        s3_csv_key = f"extracted_data/{csv_filename}"
        s3.upload_file(csv_filename, bucket_name, s3_csv_key)
        print(f"✓ CSV uploaded to S3: {s3_csv_key}")
    except Exception as e:
        print(f"✗ Error uploading CSV to S3: {str(e)}")

    return csv_filename

if __name__ == "__main__":
    print("=== Passbook Details Extractor ===")
    csv_file = process_all_passbook_documents()
    print(f"\nExtraction completed! Check the file: {csv_file}")
