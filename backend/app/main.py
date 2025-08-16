from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv
from datetime import datetime
from typing import List

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

@app.post("/upload-documents")
async def upload_documents(
    user_id: str = Form(...),
    aadhar: UploadFile = File(...),
    bank_statement: UploadFile = File(...),
    form16: UploadFile = File(...)
):
    bucket_name = os.getenv('S3_BUCKET_NAME')
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    
    files = [
        (aadhar, 'aadhar'),
        (bank_statement, 'bank'),
        (form16, 'form16')
    ]
    
    uploaded_files = []
    
    try:
        for file, doc_type in files:
            key = f"tax-documents/{user_id}/{doc_type}/{timestamp}_{file.filename}"
            
            s3_client.upload_fileobj(
                file.file,
                bucket_name,
                key,
                ExtraArgs={
                    'ContentType': file.content_type,
                    'Metadata': {
                        'user-id': user_id,
                        'document-type': doc_type,
                        'upload-date': timestamp
                    }
                }
            )
            
            uploaded_files.append({
                'document_type': doc_type,
                'filename': file.filename,
                's3_key': key,
                's3_url': f"https://{bucket_name}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/{key}"
            })
    
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"S3 upload failed: {str(e)}")
    
    return {
        'success': True,
        'message': 'Documents uploaded successfully',
        'uploaded_files': uploaded_files
    }