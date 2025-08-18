# AWS S3 Setup Guide

## Step 1: Get AWS Credentials

1. **Login to AWS Console**: Go to https://aws.amazon.com/console/
2. **Create IAM User**:
   - Go to IAM → Users → Create User
   - Username: `taxes-app-user`
   - Select "Programmatic access"
3. **Attach S3 Policy**:
   - Attach policy: `AmazonS3FullAccess` (or create custom policy)
4. **Save Credentials**:
   - Copy `Access Key ID` and `Secret Access Key`

## Step 2: Update .env File

Replace these values in `backend/.env`:

```env
AWS_ACCESS_KEY_ID=AKIA...your_actual_key
AWS_SECRET_ACCESS_KEY=your_actual_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=ocrdocstorage
```

## Step 3: Test Connection

Run the test script:
```bash
cd backend
python test_s3.py
```

## Step 4: Verify Bucket Exists

Make sure your S3 bucket `ocrdocstorage` exists in the AWS console.

## Step 5: Test API

Start your FastAPI server:
```bash
cd backend
python -m uvicorn app.main:app --reload
```

Test the connection endpoint:
```
GET http://localhost:8000/test-s3-connection
```

## Folder Structure Created

Your S3 bucket will have this structure:
```
ocrdocstorage/
├── user-id-1/
│   ├── aadhar.pdf
│   ├── bank_statement.pdf
│   └── form16.pdf
├── user-id-2/
│   ├── aadhar.pdf
│   ├── bank_statement.pdf
│   └── form16.pdf
```

## Troubleshooting

- **403 Forbidden**: Check IAM permissions
- **NoSuchBucket**: Create the bucket in AWS console
- **InvalidAccessKeyId**: Verify credentials in .env
- **SignatureDoesNotMatch**: Check secret key is correct