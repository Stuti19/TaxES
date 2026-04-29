import json
import os
from pathlib import Path

BACKEND_DIR = Path(__file__).parent
FINAL_DIR = BACKEND_DIR / "final"
FINAL_DIR.mkdir(exist_ok=True)

FORM16_PDF  = BACKEND_DIR / "form16.pdf"
PASSBOOK_PDF = BACKEND_DIR / "passbook.pdf"
AADHAR_PDF  = BACKEND_DIR / "aadhar.pdf"

# Check all PDFs exist
for pdf in [FORM16_PDF, PASSBOOK_PDF, AADHAR_PDF]:
    if not pdf.exists():
        print(f"ERROR: {pdf.name} not found in backend folder")
        exit(1)

# ── Step 1: Form16 ────────────────────────────────────────────
print("Extracting Form16...")
from form16_extractor_local import Form16ExtractorLocal
result = Form16ExtractorLocal().extract_form16_data(str(FORM16_PDF))
if result['status'] != 'success':
    print("Form16 extraction failed:", result['message']); exit(1)
form16_parsed = result['parsed']
with open(FINAL_DIR / "form16_parsed.json", "w") as f:
    json.dump(form16_parsed, f, indent=2)
print("form16_parsed.json saved")
print(json.dumps(form16_parsed, indent=2))

# ── Step 2: Passbook ──────────────────────────────────────────
print("\nWaiting 30s before next API call...")
import time; time.sleep(30)
print("Extracting Passbook...")
from passbook_extractor_local import PassbookExtractorLocal
result = PassbookExtractorLocal().extract_passbook_data(str(PASSBOOK_PDF))
if result['status'] != 'success':
    print("Passbook extraction failed:", result['message']); exit(1)
passbook_parsed = result['parsed']
with open(FINAL_DIR / "passbook_parsed.json", "w") as f:
    json.dump(passbook_parsed, f, indent=2)
print("passbook_parsed.json saved")
print(json.dumps(passbook_parsed, indent=2))

# ── Step 3: Aadhar ────────────────────────────────────────────
print("\nWaiting 30s before next API call...")
import time; time.sleep(30)
print("Extracting Aadhar...")
from aadhar_extractor_local import AadharExtractorLocal
result = AadharExtractorLocal().extract_aadhar_data(str(AADHAR_PDF))
if result['status'] != 'success':
    print("Aadhar extraction failed:", result['message']); exit(1)
aadhar_parsed = result['data']
with open(FINAL_DIR / "aadhar_parsed.json", "w") as f:
    json.dump(aadhar_parsed, f, indent=2)
print("aadhar_parsed.json saved")
print(json.dumps(aadhar_parsed, indent=2))

# ── Step 4: Fill Excel ────────────────────────────────────────
print("\nFilling Excel...")
from excel_filler_local import ExcelFiller

# Read contact info if available
contact_file = FINAL_DIR / 'contact.json'
email, mobile_no = '', ''
if contact_file.exists():
    with open(contact_file) as f:
        contact = json.load(f)
    email = contact.get('email', '')
    mobile_no = contact.get('mobile_no', '')
    print(f"Contact info: email={email}, mobile={mobile_no}")

# Point ExcelFiller to the final/ folder
filler = ExcelFiller()
filler.parsed_dir = FINAL_DIR
filler.excel_dir = FINAL_DIR

result = filler.fill_itr_excel(email=email, mobile_no=mobile_no)
if result['status'] == 'success':
    print("Excel saved to:", result['file_path'])
else:
    print("Excel generation failed:", result['message'])
