import os
import json
import shutil
from pathlib import Path
import subprocess
import sys

class DocumentProcessor:
    def __init__(self):
        self.base_dir = Path("taxes_files")
        self.uploads_dir = self.base_dir / "uploads"
        self.extracted_dir = self.base_dir / "extracted_data"
        self.parsed_dir = self.base_dir / "parsed"
        
        # Create directories if they don't exist
        for directory in [self.uploads_dir, self.extracted_dir, self.parsed_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Clear existing files to avoid duplicates
        self._clear_existing_files()

    def save_uploaded_files(self, aadhar_file, passbook_file, form16_file):
        """Save uploaded files with standardized names"""
        try:
            # Save files with standard names
            shutil.copy2(aadhar_file, self.uploads_dir / "aadhar.pdf")
            shutil.copy2(passbook_file, self.uploads_dir / "bank.pdf")
            shutil.copy2(form16_file, self.uploads_dir / "form16.pdf")
            
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

    def generate_excel(self):
        """Generate Excel file from parsed JSON data"""
        try:
            print("Starting Excel generation...")
            from excel_filler_local import ExcelFiller
            filler = ExcelFiller()
            result = filler.fill_itr_excel()
            print(f"Excel generation result: {result}")
            return result
        except Exception as e:
            print(f"Excel generation error in processor: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'status': 'error', 'message': str(e)}

    def _clear_existing_files(self):
        """Clear existing files to avoid duplicates"""
        # Clear uploads
        for file_path in self.uploads_dir.glob("*.pdf"):
            file_path.unlink(missing_ok=True)
        
        # Clear extracted data
        for file_path in self.extracted_dir.glob("*.json"):
            file_path.unlink(missing_ok=True)
        
        # Clear parsed data
        for file_path in self.parsed_dir.glob("*.json"):
            file_path.unlink(missing_ok=True)
        
        # Clear excel files
        excel_dir = self.base_dir / "excel"
        if excel_dir.exists():
            for file_path in excel_dir.glob("*.xlsx"):
                file_path.unlink(missing_ok=True)

    def process_documents(self, aadhar_file, passbook_file, form16_file):
        """Complete document processing pipeline"""
        # Step 1: Save files
        save_result = self.save_uploaded_files(aadhar_file, passbook_file, form16_file)
        if save_result['status'] != 'success':
            return save_result

        # Step 2: Run extractors
        extraction_results = self.run_extractors()
        
        # Step 3: Run parsers
        parsing_results = self.run_parsers()
        
        # Step 4: Generate Excel
        excel_result = self.generate_excel()

        return {
            'status': 'success',
            'message': 'Document processing completed',
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
                'excel': str(self.base_dir / "excel" / "filled_itr.xlsx")
            }
        }

if __name__ == "__main__":
    processor = DocumentProcessor()
    # Test with sample files
    result = processor.process_documents("sample_aadhar.pdf", "sample_bank.pdf", "sample_form16.pdf")
    print(json.dumps(result, indent=2))