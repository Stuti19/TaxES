# TaxES Document Processing Backend

This backend system processes tax documents (Aadhar, Bank Passbook, Form-16) using AWS Textract for data extraction.

## Architecture

```
Frontend Upload → Backend API → File Storage → Extractors → Parsers → JSON Output
```

### File Flow:
1. **Upload**: Files saved to `/taxes_files/uploads/` as `aadhar.pdf`, `bank.pdf`, `form16.pdf`
2. **Extraction**: AWS Textract processes files, saves JSON to `/taxes_files/extracted_data/`
3. **Parsing**: Structured data extracted, saves to `/taxes_files/parsed/`

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure AWS**:
   ```bash
   cp .env.example .env
   # Edit .env with your AWS credentials
   ```

3. **Start Server**:
   ```bash
   python start_server.py
   ```

## API Endpoints

### POST /process-documents
Processes uploaded documents through the complete pipeline.

**Request**: Multipart form with files:
- `aadhar`: Aadhar card PDF
- `passbook`: Bank passbook PDF  
- `form16`: Form-16 PDF
- `user_id`: User identifier

**Response**:
```json
{
  "success": true,
  "message": "Documents processed successfully",
  "extraction_results": {
    "form16": "success",
    "passbook": "success", 
    "aadhar": "success"
  },
  "parsing_results": {
    "form16_parser": "success",
    "passbook_parser": "success"
  },
  "output_files": {
    "extracted": {...},
    "parsed": {...}
  }
}
```

## Components

### Extractors (AWS Textract)
- `form16_extractor_local.py`: Extracts Form-16 key-value pairs
- `passbook_extractor_local.py`: Extracts bank account details
- `aadhar_extractor_local.py`: Extracts Aadhar information

### Parsers (Structured Data)
- `form16_parser.py`: Parses Form-16 into tax fields
- `passbook_parser.py`: Parses bank details into structured format

### Main Processor
- `document_processor.py`: Orchestrates the complete pipeline
- `app.py`: Flask API server

## Output Structure

### Extracted Data (`/taxes_files/extracted_data/`)
Raw key-value pairs from Textract:
```json
[
  {
    "Key": "Employee Name",
    "Value": "John Doe", 
    "Confidence": 95.2
  }
]
```

### Parsed Data (`/taxes_files/parsed/`)
Structured tax information:
```json
{
  "assessment_year": "2023-24",
  "pan": "ABCDE1234F",
  "gross_salary": 500000,
  "deduction_80C": 150000
}
```

## Requirements

- Python 3.8+
- AWS Account with Textract access
- Required Python packages (see requirements.txt)

## Error Handling

The system handles:
- Invalid file formats
- AWS service errors  
- Missing dependencies
- File processing failures

Each component returns structured error messages for debugging.