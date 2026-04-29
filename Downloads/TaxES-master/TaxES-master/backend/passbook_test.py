import json
from passbook_extractor_local import PassbookExtractorLocal
result = PassbookExtractorLocal().extract_passbook_data('taxes_files/0a8ea44d-555a-40e5-9d34-a9da1e93b82d/uploads/bank.pdf')
print('Status:', result['status'])
if result['status'] == 'success':
    print(json.dumps(result['parsed'], indent=2))
else:
    print('Error:', result['message'])
