import boto3
import os
from dotenv import load_dotenv

load_dotenv()

print("Testing AWS connection...")
print(f"AWS_ACCESS_KEY_ID: {os.getenv('AWS_ACCESS_KEY_ID')}")
print(f"AWS_REGION: {os.getenv('AWS_REGION')}")
print(f"S3_BUCKET_NAME: {os.getenv('S3_BUCKET_NAME')}")

try:
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION')
    )
    
    bucket_name = os.getenv('S3_BUCKET_NAME')
    response = s3_client.head_bucket(Bucket=bucket_name)
    print("SUCCESS: S3 connection successful!")
    
except Exception as e:
    print(f"ERROR: S3 connection failed: {e}")