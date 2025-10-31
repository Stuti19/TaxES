from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
from pathlib import Path
from document_processor import DocumentProcessor
import uuid

app = Flask(__name__)
CORS(app, origins='*')  # Allow all origins for development

# Store active sessions
active_sessions = {}

@app.route('/process-documents', methods=['POST', 'OPTIONS'])
def process_documents():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
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

        # Create session-based processor
        session_id = str(uuid.uuid4())
        processor = DocumentProcessor(session_id=session_id)
        
        # Store processor in active sessions
        active_sessions[session_id] = processor

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
        print(f"Processing documents for session: {session_id}")
        result = processor.process_documents(temp_aadhar, temp_passbook, temp_form16)
        print(f"Processing completed with status: {result.get('status', 'unknown')}")

        # Clean up temporary files
        import shutil
        shutil.rmtree(temp_dir)

        if result.get('status') == 'success':
            response_data = {
                'success': True,
                'message': 'Documents processed successfully',
                'session_id': session_id,
                'extraction_results': result.get('extraction_results', {}),
                'parsing_results': result.get('parsing_results', {}),
                'excel_result': result.get('excel_result', {}),
                'output_files': result.get('output_files', {}),
                'redirect_to': f'/output.html?session={session_id}'
            }
            print(f"Sending success response: {response_data}")
            response = jsonify(response_data)
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Content-Type'] = 'application/json'
            return response
        else:
            # Clean up failed session
            error_msg = result.get('message', 'Unknown processing error')
            print(f"Processing failed: {error_msg}")
            processor.cleanup_session()
            active_sessions.pop(session_id, None)
            return jsonify({
                'success': False,
                'message': error_msg
            }), 500

    except Exception as e:
        print(f"Server error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error processing documents: {str(e)}'
        }), 500

@app.route('/download-excel', methods=['GET'])
def download_excel():
    try:
        session_id = request.args.get('session')
        if not session_id:
            return jsonify({'error': 'Session ID required'}), 400
        
        excel_path = Path(f'taxes_files/{session_id}/excel/filled_itr.xlsx')
        print(f"Looking for Excel file at: {excel_path.absolute()}")
        print(f"File exists: {excel_path.exists()}")
        
        if excel_path.exists():
            from flask import send_file, make_response
            
            # Create response with file
            response = make_response(send_file(str(excel_path.absolute()), as_attachment=True, download_name='ITR_Form.xlsx'))
            response.headers['Access-Control-Allow-Origin'] = '*'
            
            # Schedule cleanup after response is sent
            @response.call_on_close
            def cleanup_after_download():
                try:
                    if session_id in active_sessions:
                        processor = active_sessions[session_id]
                        processor.cleanup_session()
                        active_sessions.pop(session_id, None)
                        print(f"Session {session_id} cleaned up after download")
                except Exception as e:
                    print(f"Error during cleanup: {e}")
            
            return response
        else:
            return jsonify({'error': 'Excel file not found for this session'}), 404
            
    except Exception as e:
        print(f"Download error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    response = jsonify({'status': 'healthy'})
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/test', methods=['GET', 'POST'])
def test_endpoint():
    print("Test endpoint called")
    return jsonify({'message': 'Server is working', 'method': request.method})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)