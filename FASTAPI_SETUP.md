# FastAPI S3 Integration Setup

## Backend Setup

1. **Install Python dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Configure AWS credentials in backend/.env:**
```env
AWS_ACCESS_KEY_ID=your_access_key_id_here
AWS_SECRET_ACCESS_KEY=your_secret_access_key_here
AWS_REGION=us-east-1
S3_BUCKET_NAME=your_bucket_name_here
```

3. **Start FastAPI server:**
```bash
cd backend
python run.py
```
Server will run on http://localhost:8000

## Frontend Setup

Frontend is already configured to call the FastAPI endpoint.

## How it works

1. User uploads Aadhar, Bank Statement, and Form 16
2. Clicks "Start Professional ITR Processing" button
3. Frontend sends all 3 files to FastAPI endpoint `/upload-documents`
4. FastAPI uploads files to S3 with organized structure:
   ```
   tax-documents/
   ├── {user-id}/
   │   ├── aadhar/
   │   ├── bank/
   │   └── form16/
   ```
5. Returns success response with S3 URLs

## Test the integration

1. Start backend: `cd backend && python run.py`
2. Start frontend: `cd taxes && npm run dev`
3. Upload documents and click the processing button