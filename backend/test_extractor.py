from form16_extractor import extract_form16

# Test the extractor
user_id = "38acb4ec-b36c-422b-8690-7d2a8357755e"  # Using existing user ID from S3
result = extract_form16(user_id)

print("Extraction Result:")
print(f"Status: {result['status']}")
if result['status'] == 'success':
    print(f"Extracted {result['extracted_pairs_count']} key-value pairs")
    print(f"CSV saved as: {result['csv_file']}")
    print("\nFirst 5 extracted pairs:")
    for pair in result['data'][:5]:
        print(f"  {pair['Key']}: {pair['Value']} (Confidence: {pair['Confidence']}%)")
else:
    print(f"Error: {result['message']}")