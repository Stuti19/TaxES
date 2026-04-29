import json
from aadhar_extractor_local import AadharExtractorLocal
result = AadharExtractorLocal().extract_aadhar_data('aadhar.pdf')
print('Status:', result['status'])
if result['status'] == 'success':
    print(json.dumps(result['data'], indent=2))
else:
    print('Error:', result['message'])
