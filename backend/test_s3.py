import boto3
import os
from dotenv import load_dotenv

load_dotenv()

def test_s3_connection():
    """Test S3 connection and bucket access"""
    
    # Get credentials from environment
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    region = os.getenv('AWS_REGION')
    bucket_name = os.getenv('S3_BUCKET_NAME')
    
    print("=== S3 Connection Test ===")
    print(f"Bucket: {bucket_name}")
    print(f"Region: {region}")
    print(f"Access Key: {access_key[:10]}..." if access_key else "Access Key: NOT SET")
    print(f"Secret Key: {'SET' if secret_key else 'NOT SET'}")
    print()
    
    if not all([access_key, secret_key, region, bucket_name]):
        print("ERROR: Missing AWS credentials in .env file")
        return False
    
    try:
        # Create S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        
        # Test bucket access
        print("Testing bucket access...")
        s3_client.head_bucket(Bucket=bucket_name)
        print("SUCCESS: Connected to S3 bucket!")
        
        # Test upload permissions
        print("Testing upload permissions...")
        test_key = "test-connection.txt"
        s3_client.put_object(
            Bucket=bucket_name,
            Key=test_key,
            Body=b"Test connection file",
            ContentType="text/plain"
        )
        print("SUCCESS: Upload test successful!")
        
        # Clean up test file
        s3_client.delete_object(Bucket=bucket_name, Key=test_key)
        print("SUCCESS: Cleanup successful!")
        
        return True
        
    except Exception as e:
        print(f"ERROR: S3 connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_s3_connection()