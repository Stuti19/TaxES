import json

PDF_FORM16 = "taxes_files/0a8ea44d-555a-40e5-9d34-a9da1e93b82d/uploads/form16.pdf"
PDF_PASSBOOK = "taxes_files/0a8ea44d-555a-40e5-9d34-a9da1e93b82d/uploads/bank.pdf"

print("=" * 60)
print("Testing Form16 Extractor...")
print("=" * 60)
try:
    from form16_extractor_local import Form16ExtractorLocal
    result = Form16ExtractorLocal().extract_form16_data(PDF_FORM16)
    print("Status:", result['status'])
    if result['status'] == 'success':
        print("Extracted pairs count:", result['extracted_pairs_count'])
        print("\nParsed Output:")
        print(json.dumps(result['parsed'], indent=2))
        with open("test_form16_output.json", "w") as f:
            json.dump(result, f, indent=2)
    else:
        print("Error:", result['message'])
except Exception as e:
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("Testing Passbook Extractor...")
print("=" * 60)
try:
    from passbook_extractor_local import PassbookExtractorLocal
    result = PassbookExtractorLocal().extract_passbook_data(PDF_PASSBOOK)
    print("Status:", result['status'])
    if result['status'] == 'success':
        print("Extracted pairs count:", result['extracted_pairs_count'])
        print("\nParsed Output:")
        print(json.dumps(result['parsed'], indent=2))
        with open("test_passbook_output.json", "w") as f:
            json.dump(result, f, indent=2)
    else:
        print("Error:", result['message'])
except Exception as e:
    import traceback
    traceback.print_exc()
