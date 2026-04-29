import json
from form16_extractor import Form16Extractor

def lambda_handler(event, context):
    """
    AWS Lambda handler for Form 16 extraction
    
    Expected event structure:
    {
        "user_id": "user123",
        "bucket_name": "optional-override-bucket",
        "document_key": "optional-custom-path/form16.pdf"
    }
    """
    
    try:
        user_id = event.get('user_id')
        if not user_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'user_id is required'})
            }
        
        extractor = Form16Extractor()
        
        # Override bucket if provided
        if event.get('bucket_name'):
            extractor.bucket_name = event['bucket_name']
        
        # Use custom document key if provided
        if event.get('document_key'):
            document_key = event['document_key']
        else:
            document_key = f"{user_id}/form16.pdf"
        
        # Extract data
        result = extractor.extract_form16_data(user_id)
        
        if result['status'] == 'success':
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Form 16 data extracted successfully',
                    'extracted_pairs_count': result['extracted_pairs_count'],
                    'csv_file': result['csv_file'],
                    'key_value_pairs': result['data']
                })
            }
        else:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': result['message']})
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }