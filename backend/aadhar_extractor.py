import boto3
import re
import csv
import os
from datetime import datetime
from dotenv import load_dotenv
from botocore.exceptions import ClientError

load_dotenv()

# Initialize AWS clients
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


def extract_text_from_s3_pdf(bucket, key):
    """Extract text from PDF document using Textract"""
    try:
        response = textract.detect_document_text(
            Document={'S3Object': {'Bucket': bucket, 'Name': key}}
        )
        lines = []
        for item in response['Blocks']:
            if item['BlockType'] == 'LINE':
                line = item['Text'].strip()
                # Skip Hindi lines (Devanagari characters)
                if re.search(r'[\u0900-\u097F]', line):
                    continue
                if line:
                    lines.append(line)
        return lines
    except Exception as e:
        print(f"Error extracting text from {key}: {str(e)}")
        return []


def normalize_dob(dob_str):
    """Normalize DOB into YYYY-MM-DD"""
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(dob_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return dob_str


def extract_aadhar_details(lines):
    """Extract Aadhaar card details from filtered text lines"""
    details = {
        'aadhar_number': None,
        'name': None,
        'dob': None,
        'address': None,
        'gender': None
    }

    full_text = " ".join(lines)

    # ---------- Aadhaar Number ----------
    match = re.search(r'\b(\d{4}\s?\d{4}\s?\d{4})\b', full_text)
    if match:
        details['aadhar_number'] = match.group(1).replace(" ", "")

    # ---------- DOB ----------
    dob_match = re.search(r'(?:DOB|Date of Birth)[:\s-]+(\d{1,2}[\/\-\s]\d{1,2}[\/\-\s]\d{4})', full_text, re.IGNORECASE)
    if dob_match:
        details['dob'] = normalize_dob(dob_match.group(1).replace(" ", ""))

    # ---------- Gender ----------
    for line in lines:
        if re.search(r'\b(Male|Female)\b', line, re.IGNORECASE):
            if "male" in line.lower():
                details['gender'] = "Male"
            elif "female" in line.lower():
                details['gender'] = "Female"
            break

    # ---------- Name ----------
    # Case 1: Just above DOB
    if details['dob']:
        for i, line in enumerate(lines):
            if details['dob'].split("-")[0] in line or details['dob'].replace("-", "/") in line:
                if i > 0:
                    candidate = lines[i-1].strip()
                    if len(candidate.split()) >= 2 and not any(ch.isdigit() for ch in candidate):
                        details['name'] = candidate
                break
    # Case 2: fallback - first line after "Government of India"
    if not details['name']:
        for i, line in enumerate(lines):
            if "government of india" in line.lower():
                if i+1 < len(lines):
                    candidate = lines[i+1].strip()
                    if len(candidate.split()) >= 2:
                        details['name'] = candidate
                break

    # ---------- Address ----------
    address_lines = []
    start = None
    for i, line in enumerate(lines):
        if re.search(r'Address|S/O|D/O|W/O|C/O', line, re.IGNORECASE):
            start = i
            break
    if start is not None:
        for j in range(start, min(start+10, len(lines))):
            l = lines[j].strip()
            if any(x in l.lower() for x in ["dob", "date of birth", "male", "female", "authority", "download"]):
                continue
            if re.match(r'^\d{4}\s?\d{4}\s?\d{4}$', l):  # stop at Aadhaar number
                break
            address_lines.append(l)
    if address_lines:
        details['address'] = ", ".join(address_lines)

    return details


# ---------- S3 Helpers ----------
def get_all_user_folders(bucket_name):
    """Get all user folders (user_ids) from S3 bucket"""
    try:
        response = s3.list_objects_v2(Bucket=bucket_name, Delimiter='/')
        folders = []
        if 'CommonPrefixes' in response:
            for prefix in response['CommonPrefixes']:
                folder_name = prefix['Prefix'].rstrip('/')
                folders.append(folder_name)
        return folders
    except Exception as e:
        print(f"Error listing folders: {str(e)}")
        return []


# ---------- CSV Writer ----------
def safe_csv_writer(filename, headers, rows):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row in rows:
            writer.writerow(row)


# ---------- Main Process ----------
def process_all_aadhar_documents():
    bucket_name = os.getenv('S3_BUCKET_NAME')
    if not bucket_name:
        print("Error: S3_BUCKET_NAME not found in environment variables")
        return

    print(f"Processing Aadhar documents from bucket: {bucket_name}")
    user_folders = get_all_user_folders(bucket_name)
    print(f"Found {len(user_folders)} user folders: {user_folders}")

    csv_data = []
    csv_headers = ['user_id', 'aadhar_number', 'name', 'dob', 'address', 'gender', 'processed_date', 'source_file']

    for user_id in user_folders:
        aadhar_key = f"{user_id}/aadhar.pdf"
        try:
            s3.head_object(Bucket=bucket_name, Key=aadhar_key)
            print(f"Processing Aadhar for user: {user_id}")

            lines = extract_text_from_s3_pdf(bucket_name, aadhar_key)
            if lines:
                details = extract_aadhar_details(lines)
                csv_row = [
                    user_id,
                    details.get('aadhar_number', ''),
                    details.get('name', ''),
                    details.get('dob', ''),
                    details.get('address', ''),
                    details.get('gender', ''),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    aadhar_key
                ]
                csv_data.append(csv_row)
                print(f"✓ Extracted details for {user_id}: {details}")
            else:
                print(f"✗ No text extracted for {user_id}")

        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                print(f"✗ No aadhar.pdf found for user: {user_id}")
            else:
                print(f"✗ Error processing {user_id}: {str(e)}")
        except Exception as e:
            print(f"✗ Error processing {user_id}: {str(e)}")

    csv_filename = f"aadhar_extracted_details_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    safe_csv_writer(csv_filename, csv_headers, csv_data)

    print(f"\n✓ CSV file created: {csv_filename}")
    print(f"✓ Processed {len(csv_data)} Aadhar documents")

    # Upload to S3
    try:
        s3_csv_key = f"extracted_data/{csv_filename}"
        s3.upload_file(csv_filename, bucket_name, s3_csv_key)
        print(f"✓ CSV uploaded to S3: {s3_csv_key}")
    except Exception as e:
        print(f"✗ Error uploading CSV to S3: {str(e)}")

    return csv_filename


if __name__ == "__main__":
    print("=== Aadhaar Details Extractor ===")
    csv_file = process_all_aadhar_documents()
    print(f"\nExtraction completed! Check the file: {csv_file}")
