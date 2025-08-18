import boto3
import os
import json
from datetime import datetime

s3 = boto3.client('s3')
bucket_name = 'ocrdocstorage'

def detect_doc_type(filename):
    """Detect document type based on filename"""
    filename_lower = filename.lower()
    
    if 'pan' in filename_lower:
        return 'pan'
    elif 'form16' in filename_lower or 'form_16' in filename_lower:
        return 'form16'
    elif 'salary' in filename_lower or 'payslip' in filename_lower:
        return 'salary'
    elif 'aadhar' in filename_lower or 'aadhaar' in filename_lower:
        return 'aadhar'
    else:
        # Default or ask user
        print(f"Cannot auto-detect type for: {filename}")
        doc_type = input("Enter document type (pan/form16/salary/aadhar): ").strip().lower()
        return doc_type if doc_type in ['pan', 'form16', 'salary', 'aadhar'] else 'unknown'

def upload_with_metadata(local_path, user_id, doc_type):
    """Upload file to user-specific folder structure"""
    try:
        # S3 key: {user_id}/{doc_type}.pdf
        s3_key = f"{user_id}/{doc_type}.pdf"
        
        s3.upload_file(
            local_path, 
            bucket_name, 
            s3_key,
            ExtraArgs={
                'ContentType': 'application/pdf',
                'Metadata': {
                    'user-id': user_id,
                    'document-type': doc_type,
                    'upload-date': json.dumps(datetime.now().isoformat())
                }
            }
        )
        print(f"✅ Uploaded: {s3_key} (user: {user_id}, type: {doc_type})")
        return True
    except Exception as e:
        print(f"❌ Failed to upload {s3_key}: {e}")
        return False

def upload_document(local_path, user_id, doc_type=None):
    """Upload document to user folder"""
    if not os.path.exists(local_path):
        print(f"❌ File not found: {local_path}")
        return False
    
    # Auto-detect if not provided
    if not doc_type:
        doc_type = detect_doc_type(os.path.basename(local_path))
    
    # Validate document type
    if doc_type not in ['aadhar', 'pan', 'form16']:
        print(f"❌ Invalid document type: {doc_type}")
        return False
    
    return upload_with_metadata(local_path, user_id, doc_type)

def get_document_metadata(s3_key):
    """Get document metadata from S3"""
    try:
        response = s3.head_object(Bucket=bucket_name, Key=s3_key)
        metadata = response.get('Metadata', {})
        return metadata.get('doc-type', 'unknown')
    except Exception as e:
        print(f"Error getting metadata for {s3_key}: {e}")
        return 'unknown'

def list_user_documents(user_id):
    """List documents for a specific user"""
    print(f"\n📁 Documents for user {user_id}:")
    doc_types = ['aadhar', 'pan', 'form16']
    
    for doc_type in doc_types:
        s3_key = f"{user_id}/{doc_type}.pdf"
        try:
            s3.head_object(Bucket=bucket_name, Key=s3_key)
            print(f"  ✅ {doc_type}.pdf - EXISTS")
        except:
            print(f"  ❌ {doc_type}.pdf - MISSING")

if __name__ == "__main__":
    # Example: Upload documents for a user
    user_id = "example-user-123"  # Replace with actual Supabase user ID
    
    # Example document paths (update these paths)
    documents = {
        'aadhar': r'path/to/aadhar.pdf',
        'pan': r'path/to/pan.pdf', 
        'form16': r'path/to/form16.pdf'
    }
    
    print(f"Uploading documents for user: {user_id}")
    for doc_type, doc_path in documents.items():
        if os.path.exists(doc_path):
            upload_document(doc_path, user_id, doc_type)
        else:
            print(f"Skipping non-existent file: {doc_path}")
    
    # List user documents
    list_user_documents(user_id)