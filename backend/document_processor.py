import os
import json
import shutil
from pathlib import Path
import subprocess
import sys
import uuid

class DocumentProcessor:
    def __init__(self, session_id=None):
        self.session_id = session_id or str(uuid.uuid4())
        self.base_dir = Path("taxes_files") / self.session_id
        self.uploads_dir = self.base_dir / "uploads"
        self.extracted_dir = self.base_dir / "extracted_data"
        self.parsed_dir = self.base_dir / "parsed"
        self.excel_dir = self.base_dir / "excel"
        
        # Create directories if they don't exist
        for directory in [self.uploads_dir, self.extracted_dir, self.parsed_dir, self.excel_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        print(f"Created session: {self.session_id}")

    def save_uploaded_files(self, aadhar_file, passbook_file, form16_file):
        """Save uploaded files with standardized names"""
        try:
            print(f"Saving files to: {self.uploads_dir}")
            print(f"Aadhar file: {aadhar_file}")
            print(f"Passbook file: {passbook_file}")
            print(f"Form16 file: {form16_file}")
            
            # Save files with standard names
            shutil.copy2(aadhar_file, self.uploads_dir / "aadhar.pdf")
            print("Aadhar file saved")
            shutil.copy2(passbook_file, self.uploads_dir / "bank.pdf")
            print("Passbook file saved")
            shutil.copy2(form16_file, self.uploads_dir / "form16.pdf")
            print("Form16 file saved")
            
            return {
                'status': 'success',
                'message': 'Files saved successfully',
                'files': {
                    'aadhar': str(self.uploads_dir / "aadhar.pdf"),
                    'bank': str(self.uploads_dir / "bank.pdf"),
                    'form16': str(self.uploads_dir / "form16.pdf")
                }
            }
        except Exception as e:
            print(f"Error saving files: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'status': 'error', 'message': str(e)}

    def run_extractors(self):
        """Run all extractor scripts on the uploaded files"""
        results = {}
        
        # Run Form16 extractor
        try:
            from form16_extractor_local import Form16ExtractorLocal
            extractor = Form16ExtractorLocal()
            result = extractor.extract_form16_data(str(self.uploads_dir / "form16.pdf"))
            if result['status'] == 'success':
                # Save extracted data
                with open(self.extracted_dir / "form16_extracted.json", 'w') as f:
                    json.dump(result['data'], f, indent=2)
                results['form16'] = 'success'
            else:
                results['form16'] = f"error: {result['message']}"
        except Exception as e:
            results['form16'] = f"error: {str(e)}"

        # Run Passbook extractor
        try:
            from passbook_extractor_local import PassbookExtractorLocal
            extractor = PassbookExtractorLocal()
            result = extractor.extract_passbook_data(str(self.uploads_dir / "bank.pdf"))
            if result['status'] == 'success':
                # Save extracted data
                with open(self.extracted_dir / "passbook_extracted.json", 'w') as f:
                    json.dump(result['data'], f, indent=2)
                results['passbook'] = 'success'
            else:
                results['passbook'] = f"error: {result['message']}"
        except Exception as e:
            results['passbook'] = f"error: {str(e)}"

        # Run Aadhar extractor (saves to parsed folder since it includes parsing)
        try:
            from aadhar_extractor_local import AadharExtractorLocal
            extractor = AadharExtractorLocal()
            result = extractor.extract_aadhar_data(str(self.uploads_dir / "aadhar.pdf"))
            if result['status'] == 'success':
                # Save parsed data directly to parsed folder
                with open(self.parsed_dir / "aadhar_parsed.json", 'w') as f:
                    json.dump(result['data'], f, indent=2)
                results['aadhar'] = 'success'
            else:
                results['aadhar'] = f"error: {result['message']}"
        except Exception as e:
            results['aadhar'] = f"error: {str(e)}"

        return results

    def run_parsers(self):
        """Run parser scripts on extracted JSON files"""
        results = {}
        
        # Run Form16 parser
        try:
            from form16_parser import parse_form16
            result = parse_form16("local", str(self.extracted_dir / "form16_extracted.json"))
            if result['status'] == 'success':
                # Move parsed file to parsed directory
                shutil.move("form16_parsed.json", self.parsed_dir / "form16_parsed.json")
                results['form16_parser'] = 'success'
            else:
                results['form16_parser'] = f"error: {result['message']}"
        except Exception as e:
            results['form16_parser'] = f"error: {str(e)}"

        # Run Passbook parser
        try:
            from passbook_parser import parse_passbook
            result = parse_passbook("local", str(self.extracted_dir / "passbook_extracted.json"))
            if result['status'] == 'success':
                # Move parsed file to parsed directory
                shutil.move("passbook_parsed.json", self.parsed_dir / "passbook_parsed.json")
                results['passbook_parser'] = 'success'
            else:
                results['passbook_parser'] = f"error: {result['message']}"
        except Exception as e:
            results['passbook_parser'] = f"error: {str(e)}"

        return results

    def generate_excel(self, email='', mobile_no=''):
        """Generate Excel file from parsed JSON data"""
        try:
            print("Starting Excel generation...")
            from excel_filler_local import ExcelFiller
            filler = ExcelFiller(session_id=self.session_id)
            result = filler.fill_itr_excel(email=email, mobile_no=mobile_no)
            print(f"Excel generation result: {result}")
            return result
        except Exception as e:
            print(f"Excel generation error in processor: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'status': 'error', 'message': str(e)}

    def cleanup_session(self):
        """Delete all session files and directories"""
        try:
            if self.base_dir.exists():
                shutil.rmtree(self.base_dir)
                print(f"Cleaned up session: {self.session_id}")
        except Exception as e:
            print(f"Error cleaning up session {self.session_id}: {e}")

    def process_documents(self, aadhar_file, passbook_file, form16_file, email='', mobile_no=''):
        """Complete document processing pipeline"""
        try:
            # Step 1: Save files
            print(f"Step 1: Saving files for session {self.session_id}")
            save_result = self.save_uploaded_files(aadhar_file, passbook_file, form16_file)
            if save_result['status'] != 'success':
                print(f"File save failed: {save_result['message']}")
                return save_result
            print("Files saved successfully")

            # Step 2: Run extractors
            print("Step 2: Running extractors")
            extraction_results = self.run_extractors()
            print(f"Extraction results: {extraction_results}")
            
            # Step 3: Run parsers
            print("Step 3: Running parsers")
            parsing_results = self.run_parsers()
            print(f"Parsing results: {parsing_results}")
            
            # Step 4: Generate Excel
            print("Step 4: Generating Excel")
            excel_result = self.generate_excel(email, mobile_no)
            print(f"Excel result: {excel_result}")
        except Exception as e:
            print(f"Error in process_documents: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'status': 'error', 'message': str(e)}

        return {
            'status': 'success',
            'message': 'Document processing completed',
            'session_id': self.session_id,
            'extraction_results': extraction_results,
            'parsing_results': parsing_results,
            'excel_result': excel_result,
            'output_files': {
                'extracted': {
                    'form16': str(self.extracted_dir / "form16_extracted.json"),
                    'passbook': str(self.extracted_dir / "passbook_extracted.json")
                },
                'parsed': {
                    'form16': str(self.parsed_dir / "form16_parsed.json"),
                    'passbook': str(self.parsed_dir / "passbook_parsed.json"),
                    'aadhar': str(self.parsed_dir / "aadhar_parsed.json")
                },
                'excel': str(self.excel_dir / "filled_itr.xlsx")
            }
        }

if __name__ == "__main__":
    processor = DocumentProcessor()
    # Test with sample files
    result = processor.process_documents("sample_aadhar.pdf", "sample_bank.pdf", "sample_form16.pdf")
    print(json.dumps(result, indent=2))