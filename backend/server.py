from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
from pathlib import Path
from document_processor import DocumentProcessor

app = Flask(__name__)
CORS(app)

@app.route('/process-documents', methods=['POST'])
def process_documents():
    try:
        # Check if all required files are present
        if 'aadhar' not in request.files or 'passbook' not in request.files or 'form16' not in request.files:
            return jsonify({
                'success': False,
                'message': 'Missing required files. Please upload Aadhar, Passbook, and Form16.'
            }), 400

        aadhar_file = request.files['aadhar']
        passbook_file = request.files['passbook']
        form16_file = request.files['form16']
        user_id = request.form.get('user_id', 'default_user')

        # Validate file types
        allowed_extensions = {'.pdf'}
        for file_obj, name in [(aadhar_file, 'Aadhar'), (passbook_file, 'Passbook'), (form16_file, 'Form16')]:
            if not file_obj.filename or not any(file_obj.filename.lower().endswith(ext) for ext in allowed_extensions):
                return jsonify({
                    'success': False,
                    'message': f'{name} file must be a PDF'
                }), 400

        # Create temporary files
        temp_dir = tempfile.mkdtemp()
        temp_aadhar = os.path.join(temp_dir, 'temp_aadhar.pdf')
        temp_passbook = os.path.join(temp_dir, 'temp_passbook.pdf')
        temp_form16 = os.path.join(temp_dir, 'temp_form16.pdf')

        # Save uploaded files temporarily
        aadhar_file.save(temp_aadhar)
        passbook_file.save(temp_passbook)
        form16_file.save(temp_form16)

        # Process documents
        processor = DocumentProcessor()
        result = processor.process_documents(temp_aadhar, temp_passbook, temp_form16)

        # Clean up temporary files
        import shutil
        shutil.rmtree(temp_dir)

        if result['status'] == 'success':
            return jsonify({
                'success': True,
                'message': 'Documents processed successfully',
                'extraction_results': result['extraction_results'],
                'parsing_results': result['parsing_results'],
                'excel_result': result['excel_result'],
                'output_files': result['output_files'],
                'redirect_to': '/output.html'
            })
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error processing documents: {str(e)}'
        }), 500

@app.route('/download-excel', methods=['GET'])
def download_excel():
    try:
        excel_path = Path('taxes_files/excel/filled_itr.xlsx')
        print(f"Looking for Excel file at: {excel_path.absolute()}")
        print(f"File exists: {excel_path.exists()}")
        
        if excel_path.exists():
            from flask import send_file, make_response
            response = make_response(send_file(str(excel_path.absolute()), as_attachment=True, download_name='ITR_Form.xlsx'))
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
        else:
            # Try to generate Excel if it doesn't exist
            print("Excel file not found, attempting to generate...")
            processor = DocumentProcessor()
            result = processor.generate_excel()
            
            if result['status'] == 'success' and excel_path.exists():
                from flask import send_file, make_response
                response = make_response(send_file(str(excel_path.absolute()), as_attachment=True, download_name='ITR_Form.xlsx'))
                response.headers['Access-Control-Allow-Origin'] = '*'
                return response
            else:
                return jsonify({'error': f'Excel file not found and generation failed: {result.get("message", "Unknown error")}'}), 404
    except Exception as e:
        print(f"Download error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)