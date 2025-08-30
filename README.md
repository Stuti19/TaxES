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