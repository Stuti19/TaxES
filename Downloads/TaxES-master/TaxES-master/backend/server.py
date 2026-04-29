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

        excel_path = FINAL_DIR / 'itr_pending.xlsx'
        # Note: We don't create Excel in pipeline anymore, just extract JSON files
        # Excel will be created when user completes wizard

        return jsonify({
            'success': True,
            'message': 'Documents processed! Please fill in the additional details.',
            'redirect_to': '/wizard'
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


# ────────────── USER INPUT WIZARD ENDPOINTS ──────────────

@app.route('/api/user-inputs/house-property', methods=['POST', 'OPTIONS'])
def save_house_property():
    """Save and validate house property input"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    try:
        from input_validator import InputValidator
        import json
        
        data = request.get_json()
        is_valid, error_msg, cleaned_data = InputValidator.validate_house_property(data)
        
        if not is_valid:
            return jsonify({'success': False, 'message': error_msg}), 400
        
        # Save to session file
        user_inputs_path = FINAL_DIR / 'user_inputs.json'
        user_inputs = {}
        
        if user_inputs_path.exists():
            with open(user_inputs_path, 'r') as f:
                user_inputs = json.load(f)
        
        user_inputs['house_property'] = cleaned_data
        
        with open(user_inputs_path, 'w') as f:
            json.dump(user_inputs, f, indent=2)
        
        print(f"House Property input saved: {cleaned_data}")
        return jsonify({'success': True, 'message': 'House property data saved'})
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/user-inputs/other-income', methods=['POST', 'OPTIONS'])
def save_other_income():
    """Save and validate other income input"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    try:
        from input_validator import InputValidator
        import json
        
        data = request.get_json()
        is_valid, error_msg, cleaned_data = InputValidator.validate_other_income(data)
        
        if not is_valid:
            return jsonify({'success': False, 'message': error_msg}), 400
        
        # Save to session file
        user_inputs_path = FINAL_DIR / 'user_inputs.json'
        user_inputs = {}
        
        if user_inputs_path.exists():
            with open(user_inputs_path, 'r') as f:
                user_inputs = json.load(f)
        
        user_inputs['other_income'] = cleaned_data
        
        with open(user_inputs_path, 'w') as f:
            json.dump(user_inputs, f, indent=2)
        
        print(f"Other Income input saved: {cleaned_data}")
        return jsonify({'success': True, 'message': 'Other income data saved'})
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/user-inputs/deductions', methods=['POST', 'OPTIONS'])
def save_deductions():
    """Save and validate deductions input"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    try:
        from input_validator import InputValidator
        import json
        
        data = request.get_json()
        is_valid, error_msg, cleaned_data = InputValidator.validate_deductions(data)
        
        if not is_valid:
            return jsonify({'success': False, 'message': error_msg}), 400
        
        # Save to session file
        user_inputs_path = FINAL_DIR / 'user_inputs.json'
        user_inputs = {}
        
        if user_inputs_path.exists():
            with open(user_inputs_path, 'r') as f:
                user_inputs = json.load(f)
        
        user_inputs['deductions'] = cleaned_data
        
        with open(user_inputs_path, 'w') as f:
            json.dump(user_inputs, f, indent=2)
        
        print(f"Deductions input saved: {cleaned_data}")
        return jsonify({'success': True, 'message': 'Deductions data saved'})
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/fill-excel-with-inputs', methods=['POST', 'OPTIONS'])
def fill_excel_with_inputs():
    """Fill pending Excel with user input sections"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    try:
        import json
        from excel_filler_local import ExcelFiller
        
        # Ensure final directory exists
        FINAL_DIR.mkdir(exist_ok=True)
        
        # Check if files exist with detailed error messages
        user_inputs_path = FINAL_DIR / 'user_inputs.json'
        
        print(f"Checking for user_inputs.json at: {user_inputs_path}")
        print(f"Exists: {user_inputs_path.exists()}")
        
        # List all files in final directory
        print(f"Files in {FINAL_DIR}:")
        if FINAL_DIR.exists():
            for f in FINAL_DIR.iterdir():
                print(f"  - {f.name}")
        
        if not user_inputs_path.exists():
            return jsonify({
                'success': False, 
                'message': 'No user inputs found. Please complete all form steps first.',
                'missing_file': 'user_inputs.json'
            }), 400
        
        # Load and validate user inputs
        with open(user_inputs_path, 'r') as f:
            user_inputs = json.load(f)
        
        # Check if all three sections are present
        missing_sections = []
        if 'house_property' not in user_inputs or not user_inputs['house_property']:
            missing_sections.append('House Property')
        if 'other_income' not in user_inputs or not user_inputs['other_income']:
            missing_sections.append('Other Income')
        if 'deductions' not in user_inputs or not user_inputs['deductions']:
            missing_sections.append('Deductions')
        
        if missing_sections:
            return jsonify({
                'success': False,
                'message': f'Missing required sections: {", ".join(missing_sections)}. Please complete all form steps.',
                'missing_sections': missing_sections
            }), 400
        
        # Load contact info if available
        contact_file = FINAL_DIR / 'contact.json'
        email, mobile_no = '', ''
        if contact_file.exists():
            with open(contact_file) as f:
                contact = json.load(f)
            email = contact.get('email', '')
            mobile_no = contact.get('mobile_no', '')
        
        # Fill complete ITR: Merge extracted data + user inputs
        filler = ExcelFiller()
        filler.parsed_dir = FINAL_DIR
        filler.excel_dir = FINAL_DIR
        
        result = filler.fill_itr_complete(
            parsed_data_dir=str(FINAL_DIR),
            user_inputs=user_inputs,
            email=email,
            mobile_no=mobile_no
        )
        
        if result['status'] != 'success':
            return jsonify({'success': False, 'message': result['message']}), 500
        
        print(f"Complete ITR generated: {result['file_path']}")
        return jsonify({'success': True, 'message': 'Complete ITR form filled successfully'})
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)
