from aadhar_extractor import extract_aadhar_details, extract_text_from_s3_pdf
from passbook_extractor import extract_passbook_details
import os
from dotenv import load_dotenv

load_dotenv()

def debug_user_data(user_id):
    bucket_name = os.getenv('S3_BUCKET_NAME')
    
    print(f"=== Debugging {user_id} ===")
    
    # Debug Aadhaar
    aadhar_key = f"{user_id}/aadhar.pdf"
    try:
        lines = extract_text_from_s3_pdf(bucket_name, aadhar_key)
        print(f"Aadhaar lines extracted: {len(lines)}")
        if lines:
            aadhar_details = extract_aadhar_details(lines)
            print(f"Aadhaar details: {aadhar_details}")
    except Exception as e:
        print(f"Aadhaar error: {e}")
    
    # Debug Passbook
    passbook_key = f"{user_id}/passbook.pdf"
    try:
        lines = extract_text_from_s3_pdf(bucket_name, passbook_key)
        print(f"Passbook lines extracted: {len(lines)}")
        if lines:
            passbook_details = extract_passbook_details(lines)
            print(f"Passbook details: {passbook_details}")
    except Exception as e:
        print(f"Passbook error: {e}")

if __name__ == "__main__":
    debug_user_data("38acb4ec-b36c-422b-8690-7d2a8357755e")