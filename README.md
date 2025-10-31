# Form 16 Key-Value Extractor Lambda

This Lambda function uses AWS Textract to extract all key-value pairs from Form 16 documents and saves them to a CSV file.

## Features

- Extracts all key-value pairs from Form 16 using AWS Textract
- No regex patterns - relies entirely on Textract's ML capabilities
- Outputs results to CSV format
- Includes confidence scores for each extraction
- Handles documents stored in S3

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create deployment package:**
   ```bash
   python deployment_package.py
   ```

3. **Deploy to AWS Lambda:**
   - Upload `form16_extractor_lambda.zip`
   - Set handler to `form16_extractor_lambda.lambda_handler`
   - Set timeout to 5 minutes
   - Attach the IAM policy from `iam_policy.json`

## Usage

### Event Structure
```json
{
    "bucket_name": "your-input-bucket",
    "document_key": "form16.pdf",
    "output_bucket": "your-output-bucket",
    "output_key": "extracted_form16_data.csv"
}
```

### Response Structure
```json
{
    "statusCode": 200,
    "body": {
        "message": "Form 16 data extracted successfully",
        "extracted_pairs_count": 25,
        "output_location": "s3://your-output-bucket/extracted_form16_data.csv",
        "key_value_pairs": [...]
    }
}
```

## CSV Output Format

The generated CSV contains three columns:
- **Key**: The field name/label extracted from the form
- **Value**: The corresponding value for that field
- **Confidence**: Textract's confidence score (0-100)

## Common Form 16 Fields Extracted

- Employee Name
- PAN Number
- Employee Code
- Designation
- Department
- Assessment Year
- Financial Year
- Employer Details (Name, Address, TAN)
- Salary Components (Basic, HRA, Allowances)
- Deductions (PF, ESI, Professional Tax)
- Tax Deducted at Source (TDS)
- Form 16A Details

## Requirements

- AWS Lambda runtime: Python 3.9+
- Required AWS services: Textract, S3
- Input document formats: PDF, PNG, JPEG
- Maximum document size: 10MB (Textract limit)

## Error Handling

The function handles:
- Missing input parameters
- Textract service errors
- S3 access issues
- Invalid document formats

## Cost Considerations

- Textract charges per page analyzed
- S3 storage and transfer costs
- Lambda execution time charges

Estimated cost: ~$0.015 per Form 16 document (1-2 pages)

---

# TaxES Complete Project Flow

## Project Overview

TaxES is an end-to-end automated ITR (Income Tax Return) filing system that uses AI-powered document extraction to process tax documents and generate completed Excel ITR forms.

## Complete System Architecture

```
User Upload → File Storage → AI Extraction → Data Parsing → Excel Generation → Download
     ↓              ↓             ↓             ↓              ↓             ↓
  Frontend      Local Files    AWS Textract   Structured    ITR Excel    User Gets
  Dashboard    /taxes_files/   + Groq API     JSON Data     Template     Final File
```

## Detailed User Flow

### 1. Document Upload (Frontend)
- **Location**: React Dashboard (`taxes/src/pages/Dashboard.tsx`)
- **User Action**: Upload 3 PDF files:
  - Aadhar Card
  - Bank Passbook 
  - Form-16
- **Validation**: 
  - PDF format only
  - Max 10MB per file
  - All 3 files required
- **API Call**: POST to `/process-documents`

### 2. File Storage (Backend)
- **Location**: `/taxes_files/uploads/`
- **Files Saved As**:
  - `aadhar.pdf`
  - `bank.pdf` 
  - `form16.pdf`
- **Behavior**: Overwrites existing files (no duplicates)

### 3. AI-Powered Extraction

#### AWS Textract Processing:
- **Form-16**: Extracts salary, tax, deduction details
- **Passbook**: Extracts bank account information
- **Output**: Raw key-value pairs with confidence scores
- **Storage**: `/taxes_files/extracted_data/`
  - `form16_extracted.json`
  - `passbook_extracted.json`

#### Aadhar Processing:
- **Method**: OCR + Pattern Recognition
- **Extracts**: Name, DOB, Gender, Address, Aadhar Number
- **Direct Output**: Structured data (no separate extraction step)

### 4. Intelligent Data Parsing

#### Groq API Integration:
- **Purpose**: Parse name and address into structured components
- **Name Parsing**: "Anjali" → {first_name: "Anjali", middle_name: "", last_name: ""}
- **Address Parsing**: Complex address → Structured components:
  - Flat/Door/Block Number
  - Building/Village Name
  - Road/Street
  - Area/Locality
  - City/District
  - State (validated against Indian states)
  - PIN Code

#### Structured Data Output:
- **Location**: `/taxes_files/parsed/`
- **Files**:
  - `form16_parsed.json` - Tax and salary data
  - `passbook_parsed.json` - Bank details
  - `aadhar_parsed.json` - Personal information

### 5. Excel ITR Generation
- **Template**: `itr_temp.xlsx` (ITR form template)
- **Process**: Maps parsed JSON data to specific Excel cells
- **Calculations**: Automatic tax calculations:
  - Tax Payable After Rebate = Tax on Total Income - Rebate 87A
  - Total Tax and Cess = Tax Payable + Health Education Cess
  - Balance Tax After Relief = Total Tax - Relief Section 89
- **Output**: `/taxes_files/excel/filled_itr.xlsx`

### 6. User Download
- **Auto-Redirect**: User automatically redirected to `/output.html`
- **Download**: Click "Download ITR Excel" button
- **File Served**: Completed Excel ITR form

## Technical Requirements

### Backend Dependencies
```bash
flask==2.3.3
flask-cors==4.0.0
boto3==1.28.85
python-dotenv==1.0.0
PyMuPDF==1.23.8
Pillow==10.0.1
easyocr==1.7.0
openpyxl==3.1.2
requests==2.31.0
```

### Environment Variables
```bash
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=us-east-1
S3_BUCKET_NAME=your_bucket
GROQ_API_KEY=your_groq_key
```

### API Keys Required
1. **AWS Account**: For Textract service
2. **Groq API**: Free account at https://console.groq.com/

## File Structure

```
TaxES/
├── backend/
│   ├── taxes_files/
│   │   ├── uploads/           # User uploaded PDFs
│   │   ├── extracted_data/    # Raw Textract output
│   │   ├── parsed/           # Structured JSON data
│   │   └── excel/            # Generated ITR Excel
│   ├── server.py             # Flask API server
│   ├── document_processor.py # Main orchestrator
│   ├── *_extractor_local.py  # AI extraction modules
│   ├── *_parser.py          # Data parsing modules
│   ├── excel_filler_local.py # Excel generation
│   ├── groq_parser.py       # AI name/address parsing
│   └── itr_temp.xlsx        # ITR form template
└── taxes/
    ├── src/pages/Dashboard.tsx # Upload interface
    └── public/output.html     # Download page
```

## Setup Instructions

### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
python start_server.py
```

### 2. Frontend Setup
```bash
cd taxes
npm install
npm run dev
```

### 3. Get API Keys
- **AWS**: Create IAM user with Textract permissions
- **Groq**: Sign up at https://console.groq.com/ (free)

## Data Processing Details

### Form-16 Fields Extracted
- Assessment Year, PAN, Employee Details
- Gross Salary (Section 17(1), 17(2), 17(3))
- Exemptions (Section 10)
- Deductions (80C, 80D, 80E, 80G, etc.)
- Tax Calculations (TDS, Rebates, Cess)

### Passbook Fields Extracted
- Account Holder Name
- Account Number
- Bank Name (auto-detected from IFSC)
- IFSC Code

### Aadhar Fields Extracted
- Full Name (parsed into components)
- Date of Birth
- Gender
- Complete Address (parsed into components)
- Aadhar Number

## Error Handling

- **File Validation**: Format and size checks
- **API Failures**: Fallback parsing methods
- **Missing Data**: Graceful handling with empty values
- **Calculation Errors**: Safe numeric operations

## Security Features

- **Local Processing**: Files processed locally, not stored in cloud
- **Temporary Storage**: Files overwritten on each upload
- **API Security**: Secure API key management
- **CORS Protection**: Proper cross-origin handling

## Performance

- **Processing Time**: ~30-60 seconds for 3 documents
- **File Size Limit**: 10MB per document (Textract limit)
- **Concurrent Users**: Supports multiple users (files isolated)

## Cost Estimation

- **AWS Textract**: ~$0.015 per document page
- **Groq API**: Free tier (generous limits)
- **Total per ITR**: ~$0.045 (3 documents × $0.015)

This system provides a complete, automated solution for ITR filing with minimal manual intervention and high accuracy through AI-powered extraction.