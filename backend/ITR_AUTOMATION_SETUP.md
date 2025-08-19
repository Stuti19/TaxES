# ITR Automation Setup Guide

This system combines your Aadhaar and passbook extractors to automatically fill ITR templates with extracted data.

## Files Created

1. **`itr_data_mapper.py`** - Main mapper that combines both extractors
2. **`itr_mapping_config.py`** - Configuration for field-to-cell mapping
3. **`run_itr_automation.py`** - Interactive runner script
4. **Updated `requirements.txt`** - Added Excel handling dependencies

## Setup Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Place Your ITR Template
- Put your ITR template Excel file in the `backend` directory
- Name it something with "itr" in the filename (e.g., `itr_template.xlsx`)

### 3. Configure Field Mapping

Open `itr_mapping_config.py` and update the cell addresses where each field should go:

```python
DEFAULT_MAPPING = {
    'name': 'B8',           # Cell where name should go
    'aadhar_number': 'B10', # Cell where Aadhaar number should go
    'dob': 'B12',           # Cell where date of birth should go
    'gender': 'B16',        # Cell where gender should go
    'address': 'B14',       # Cell where address should go
    'accountNumber': 'B20', # Cell where account number should go
    'bankName': 'B22',      # Cell where bank name should go
    'IFSC_Code': 'B24',     # Cell where IFSC code should go
}
```

### 4. How to Find Cell Addresses

1. Open your ITR template in Excel
2. Click on the cell where you want a field to appear
3. Look at the cell reference (e.g., B8, C15, AB25)
4. Update the mapping configuration

## Usage

### Option 1: Interactive Mode
```bash
python run_itr_automation.py
```

### Option 2: Direct Usage
```python
from itr_data_mapper import ITRDataMapper

# Initialize mapper
mapper = ITRDataMapper("your_itr_template.xlsx")

# Process single user
output_path = mapper.process_user_itr("user123", "your-s3-bucket")

# Process all users
processed_files = mapper.process_all_users("your-s3-bucket")
```

## Output

- Filled ITR templates are saved in the `filled_templates/` directory
- Each file is named: `ITR_{user_id}_{timestamp}.xlsx`
- Original template remains unchanged

## Customization

### Adding New Fields

If you extract additional fields, add them to the mapping:

```python
# In itr_mapping_config.py
DEFAULT_MAPPING = {
    # ... existing fields ...
    'pan_number': 'B26',    # If you extract PAN
    'mobile': 'B28',        # If you extract mobile
    'email': 'B30',         # If you extract email
}
```

### Different Worksheets

If your ITR template has multiple sheets, modify the mapper:

```python
# In itr_data_mapper.py, update map_data_to_template method
worksheet = workbook['Sheet2']  # Specify sheet name
```

## Troubleshooting

1. **Template not found**: Ensure your Excel file has "itr" in the filename
2. **Cell mapping errors**: Verify cell addresses are correct (e.g., 'B8', not 'b8')
3. **Permission errors**: Ensure the template file is not open in Excel
4. **S3 errors**: Check your AWS credentials in `.env` file

## Example Workflow

1. User uploads Aadhaar and passbook PDFs to S3
2. Run the automation: `python run_itr_automation.py`
3. System extracts data from both documents
4. Data is mapped to the ITR template
5. Filled template is saved with user ID and timestamp