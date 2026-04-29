from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv
from datetime import datetime
from typing import List
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from form16_extractor import extract_form16
from pydantic import BaseModel

load_dotenv()

app = FastAPI()

class Form16Request(BaseModel):
    user_id: str

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8080", "http://localhost:8081", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

@app.options("/upload-documents")
async def upload_documents_options():
    return {"message": "OK"}

@app.post("/upload-documents")
async def upload_documents(
    user_id: str = Form(...),
    aadhar: UploadFile = File(...),
    pan: UploadFile = File(...),
    form16: UploadFile = File(...)
):
    bucket_name = os.getenv('S3_BUCKET_NAME')
    
    print(f"Upload request - User ID: {user_id}, Bucket: {bucket_name}")
    
    # Validate environment variables
    if not bucket_name:
        raise HTTPException(status_code=500, detail="S3_BUCKET_NAME not configured")
    
    # Validate PDF files
    files = [(aadhar, 'aadhar'), (pan, 'pan'), (form16, 'form16')]
    for file, doc_type in files:
        print(f"File: {file.filename}, Type: {doc_type}, Size: {file.size}")
        if not file.filename or not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail=f"{doc_type} must be a PDF file")
    
    uploaded_files = []
    
    try:
        for file, doc_type in files:
            # Reset file pointer
            await file.seek(0)
            
            # S3 key structure: {user_id}/{doc_type}.pdf
            key = f"{user_id}/{doc_type}.pdf"
            print(f"Uploading to S3 key: {key}")
            
            s3_client.upload_fileobj(
                file.file,
                bucket_name,
                key,
                ExtraArgs={
                    'ContentType': 'application/pdf',
                    'Metadata': {
                        'user-id': user_id,
                        'document-type': doc_type,
                        'upload-date': datetime.now().isoformat()
                    }
                }
            )
            
            print(f"Successfully uploaded: {key}")
            
            uploaded_files.append({
                'document_type': doc_type,
                'filename': f"{doc_type}.pdf",
                's3_key': key,
                's3_url': f"https://{bucket_name}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/{key}"
            })
    
    except ClientError as e:
        print(f"S3 ClientError: {e}")
        raise HTTPException(status_code=500, detail=f"S3 upload failed: {str(e)}")
    except Exception as e:
        print(f"General error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    
    return {
        'success': True,
        'message': 'Documents uploaded successfully',
        'uploaded_files': uploaded_files
    }

@app.get("/user-documents/{user_id}")
async def get_user_documents(user_id: str):
    """Check which documents exist for a user"""
    bucket_name = os.getenv('S3_BUCKET_NAME')
    doc_types = ['aadhar', 'pan', 'form16']
    documents = {}
    
    for doc_type in doc_types:
        key = f"{user_id}/{doc_type}.pdf"
        try:
            s3_client.head_object(Bucket=bucket_name, Key=key)
            documents[doc_type] = {
                'exists': True,
                's3_key': key,
                's3_url': f"https://{bucket_name}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/{key}"
            }
        except ClientError:
            documents[doc_type] = {'exists': False}
    
    return {
        'user_id': user_id,
        'documents': documents
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Server is running"}

@app.get("/test-s3-connection")
async def test_s3_connection():
    """Test S3 connection"""
    bucket_name = os.getenv('S3_BUCKET_NAME')
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        return {
            'success': True,
            'message': f'Successfully connected to S3 bucket: {bucket_name}',
            'bucket': bucket_name,
            'region': os.getenv('AWS_REGION')
        }
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"S3 connection failed: {str(e)}")

@app.post("/extract-form16")
async def extract_form16_data(request: Form16Request):
    try:
        result = extract_form16(request.user_id)
        
        if result['status'] == 'error':
            raise HTTPException(status_code=400, detail=result['message'])
        
        return {
            "message": "Form 16 data extracted successfully",
            "extracted_pairs_count": result['extracted_pairs_count'],
            "csv_file": result['csv_file'],
            "key_value_pairs": result['data']
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))