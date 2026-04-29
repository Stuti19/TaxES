from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import subprocess
import sys
from pathlib import Path

app = Flask(__name__)
CORS(app, origins='*')

BACKEND_DIR = Path(__file__).parent
FINAL_DIR = BACKEND_DIR / "final"


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})


@app.route('/process-documents', methods=['POST', 'OPTIONS'])
def process_documents():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    try:
        # Validate files
        if 'aadhar' not in request.files or 'passbook' not in request.files or 'form16' not in request.files:
            return jsonify({'success': False, 'message': 'Missing required files'}), 400

        aadhar_file  = request.files['aadhar']
        passbook_file = request.files['passbook']
        form16_file  = request.files['form16']

        for f, name in [(aadhar_file, 'Aadhar'), (passbook_file, 'Passbook'), (form16_file, 'Form16')]:
            if not f.filename.lower().endswith('.pdf'):
                return jsonify({'success': False, 'message': f'{name} must be a PDF'}), 400

        # Save directly to backend folder with fixed names
        aadhar_file.save(str(BACKEND_DIR / 'aadhar.pdf'))
        passbook_file.save(str(BACKEND_DIR / 'passbook.pdf'))
        form16_file.save(str(BACKEND_DIR / 'form16.pdf'))
        print("PDFs saved to backend folder")

        # Save email and mobile for pipeline to use
        email = request.form.get('email', '')
        mobile_no = request.form.get('mobile_no', '')
        FINAL_DIR.mkdir(exist_ok=True)
        import json
        with open(FINAL_DIR / 'contact.json', 'w') as f:
            json.dump({'email': email, 'mobile_no': mobile_no}, f)
        print(f"Contact info saved: email={email}, mobile={mobile_no}")

        # Run the pipeline
        print("Running pipeline...")
        result = subprocess.run(
            [sys.executable, str(BACKEND_DIR / 'run_pipeline.py')],
            cwd=str(BACKEND_DIR),
            capture_output=False,  # show output directly in terminal
            text=True,
            timeout=600
        )

        excel_path = FINAL_DIR / 'filled_itr.xlsx'
        if not excel_path.exists():
            return jsonify({'success': False, 'message': 'Excel file not generated'}), 500

        return jsonify({
            'success': True,
            'message': 'Documents processed successfully',
            'redirect_to': '/output.html'
        })

    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'message': 'Processing timed out (10 min limit)'}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/download-excel', methods=['GET'])
def download_excel():
    excel_path = FINAL_DIR / 'filled_itr.xlsx'
    if not excel_path.exists():
        return jsonify({'error': 'File not found'}), 404

    response = send_file(str(excel_path.absolute()), as_attachment=True, download_name='ITR_Form.xlsx')
    response.headers['Access-Control-Allow-Origin'] = '*'

    @response.call_on_close
    def cleanup():
        # Delete uploaded PDFs from backend folder
        for pdf in ['aadhar.pdf', 'passbook.pdf', 'form16.pdf']:
            pdf_path = BACKEND_DIR / pdf
            if pdf_path.exists():
                pdf_path.unlink()
                print(f"Deleted {pdf}")
        # Delete parsed JSONs from final folder
        for f in FINAL_DIR.glob('*.json'):
            f.unlink()
            print(f"Deleted {f.name}")
        print("Cleanup complete")

    return response


@app.route('/preview-excel', methods=['GET'])
def preview_excel():
    """Serve excel file inline for preview"""
    excel_path = FINAL_DIR / 'filled_itr.xlsx'
    if not excel_path.exists():
        return jsonify({'error': 'File not found'}), 404
    response = send_file(str(excel_path.absolute()), as_attachment=False, download_name='ITR_Form.xlsx')
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)
