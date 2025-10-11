"""
Aadhaar Card Data Extractor - Fixed Address Extraction
Correctly extracts Address from page 2, ignoring Hindi text
"""

import re
import sys
import json
from pathlib import Path


class AadhaarExtractor:
    def __init__(self):
        self.extracted_data = {
            'aadhaar_number': None,
            'name': None,
            'dob': None,
            'gender': None,
            'address': None,
            'raw_text': ''
        }
        self.ocr_reader = None

    def install_requirements(self):
        """Install required packages if missing"""
        packages = [
            ('fitz', 'PyMuPDF'),
            ('easyocr', 'easyocr'),
            ('PIL', 'Pillow')
        ]
        import subprocess
        for module, pip_name in packages:
            try:
                __import__(module)
            except ImportError:
                print(f"Installing {pip_name}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])

    def get_ocr_reader(self):
        """Initialize EasyOCR reader"""
        if self.ocr_reader is None:
            import easyocr
            print("Loading EasyOCR model...")
            self.ocr_reader = easyocr.Reader(['en'], gpu=False, verbose=False)
        return self.ocr_reader

    def clean_text_line(self, line):
        """Clean unwanted characters and Hindi text"""
        # Remove Hindi/Devanagari characters
        line = re.sub(r'[\u0900-\u097F]+', '', line)
        # Remove other non-English characters but keep alphanumeric, spaces, and common punctuation
        line = re.sub(r'[^A-Za-z0-9\s,./-]+', ' ', line)
        # Remove extra spaces
        line = ' '.join(line.split()).strip()
        return line

    def extract_aadhaar_number(self, text):
        """Extract 12-digit Aadhaar number"""
        patterns = [
            r'\b(\d{4})\s+(\d{4})\s+(\d{4})\b',
            r'\b(\d{4})-(\d{4})-(\d{4})\b',
            r'\b(\d{12})\b'
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for m in matches:
                num = ''.join(m) if isinstance(m, tuple) else m
                if len(num) == 12 and num.isdigit() and num[0] not in ['0', '1']:
                    return f"{num[:4]} {num[4:8]} {num[8:]}"
        return None

    def extract_dob(self, text):
        """Extract DOB in dd/mm/yyyy or dd-mm-yyyy"""
        patterns = [
            r'DOB[\s:]*(\d{2})[\/\-](\d{2})[\/\-](\d{4})',
            r'Birth[\s:]*(\d{2})[\/\-](\d{2})[\/\-](\d{4})',
            r'\b(\d{2})[\/\-](\d{2})[\/\-](19|20\d{2})\b'
        ]
        for pat in patterns:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                return f"{match.group(1)}/{match.group(2)}/{match.group(3)}"
        return None

    def extract_name(self, text):
        """Extract name from line above DOB"""
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        for i, line in enumerate(lines):
            if 'DOB' in line.upper() or re.search(r'\d{2}[\/\-]\d{2}[\/\-]\d{4}', line):
                for j in range(i - 1, max(-1, i - 4), -1):
                    prev = self.clean_text_line(lines[j])
                    if re.match(r'^[A-Za-z\s.]{3,50}$', prev):
                        return prev.strip()
        return None

    def extract_gender(self, text):
        """Extract gender (handles IFEMALE, IMALE, etc.)"""
        text_u = text.upper()
        if re.search(r'I?FEMALE', text_u):
            return "Female"
        if re.search(r'I?MALE', text_u) and 'FEMALE' not in text_u:
            return "Male"
        return None

    def extract_address(self, text):
        """Extract address from page 2 after 'Address' keyword"""
        # Clean all lines and filter Hindi text
        lines = [self.clean_text_line(l) for l in text.split('\n') if l.strip()]
        
        address_lines = []
        found_address_keyword = False
        
        for i, line in enumerate(lines):
            line_upper = line.upper()
            
            # Look for "Address" keyword (case-insensitive, allow variations)
            if re.search(r'\bADDRESS\b', line_upper) and len(line) < 30:
                found_address_keyword = True
                # Check if address content is on the same line after ":"
                if ':' in line:
                    after_colon = line.split(':', 1)[1].strip()
                    if len(after_colon) > 3:
                        address_lines.append(after_colon)
                continue
            
            # Once we find "Address", collect subsequent lines
            if found_address_keyword:
                # Skip empty or very short lines
                if len(line) < 3:
                    continue
                
                # Skip lines that look like Aadhaar numbers
                if re.search(r'\d{4}\s?\d{4}\s?\d{4}', line):
                    continue
                
                # Skip lines with government/UIDAI text
                if any(keyword in line_upper for keyword in ['GOVERNMENT', 'UIDAI', 'UNIQUE', 'ISSUED']):
                    continue
                
                # Good indicators this is address content
                is_address_line = any([
                    re.search(r'\b\d{6}\b', line),  # PIN code
                    any(w in line_upper for w in ['S/O', 'C/O', 'D/O', 'W/O']),  # Relations
                    any(w in line_upper for w in ['DIST', 'DISTRICT', 'STATE', 'VILLAGE', 'CITY', 'TOWN']),
                    ',' in line,  # Commas often in addresses
                    re.search(r'\b(ROAD|STREET|LANE|COLONY|NAGAR|GANJ|PUR)\b', line_upper),
                    len(line) > 10  # Substantial content
                ])
                
                if is_address_line:
                    address_lines.append(line)
                    
                # Stop after collecting enough lines or hitting certain patterns
                if len(address_lines) >= 5:
                    break
                    
                # Stop if we hit what looks like another section
                if any(keyword in line_upper for keyword in ['ENROLLMENT', 'DOWNLOAD', 'HELP']):
                    break
        
        # Fallback: if no address found via keyword, look for PIN code pattern
        if not address_lines:
            for i, line in enumerate(lines):
                if re.search(r'\b\d{6}\b', line):
                    # Collect this line and a few before it
                    start = max(0, i - 3)
                    for j in range(start, min(i + 2, len(lines))):
                        clean_line = lines[j]
                        if (len(clean_line) > 5 and 
                            not re.search(r'\d{4}\s?\d{4}\s?\d{4}', clean_line) and
                            not any(k in clean_line.upper() for k in ['GOVERNMENT', 'UIDAI'])):
                            address_lines.append(clean_line)
                    if address_lines:
                        break
        
        # Join and clean final address
        if address_lines:
            # Remove duplicates while preserving order
            seen = set()
            unique_lines = []
            for line in address_lines:
                if line not in seen:
                    seen.add(line)
                    unique_lines.append(line)
            
            return ', '.join(unique_lines)
        
        return None

    def process_pdf(self, pdf_path):
        """Try to extract text directly, fallback to OCR"""
        import fitz
        from PIL import Image
        import io, os
        text = ''
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text() + "\n"
        if len(text.strip()) > 50:
            return text
        print("Direct extraction failed, using OCR...")
        reader = self.get_ocr_reader()
        for i, page in enumerate(fitz.open(pdf_path)):
            pix = page.get_pixmap(matrix=fitz.Matrix(3, 3))
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            temp = f"temp_{i}.png"
            img.save(temp)
            text += "\n".join(reader.readtext(temp, detail=0)) + "\n"
            os.remove(temp)
        return text

    def extract_from_file(self, file_path):
        """Extract all Aadhaar fields from PDF"""
        file_path = Path(file_path)
        if not file_path.exists():
            print("File not found!")
            return None
        raw_text = self.process_pdf(file_path)
        if not raw_text or len(raw_text.strip()) < 10:
            print("Could not extract text.")
            return None
        self.extracted_data['raw_text'] = raw_text
        self.extracted_data['aadhaar_number'] = self.extract_aadhaar_number(raw_text)
        self.extracted_data['dob'] = self.extract_dob(raw_text)
        self.extracted_data['name'] = self.extract_name(raw_text)
        self.extracted_data['gender'] = self.extract_gender(raw_text)
        self.extracted_data['address'] = self.extract_address(raw_text)
        return self.extracted_data

    def print_results(self):
        """Print extracted info neatly"""
        print("\n" + "=" * 50)
        print("EXTRACTED AADHAAR INFORMATION")
        print("=" * 50)
        for key, val in self.extracted_data.items():
            if key != 'raw_text':
                print(f"{key.title()}: {val or 'Not Found'}")
        print("=" * 50 + "\n")


def main():
    print("\n" + "=" * 60)
    print("AADHAAR CARD DATA EXTRACTOR - FIXED ADDRESS VERSION")
    print("=" * 60)
    extractor = AadhaarExtractor()
    extractor.install_requirements()
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = input("\nEnter Aadhaar PDF path: ").strip().strip('"\'')
    
    result = extractor.extract_from_file(file_path)
    if result:
        extractor.print_results()
        
        # Save to aadhar_parsed.json
        output_data = {k: v for k, v in result.items() if k != 'raw_text'}
        with open('aadhar_parsed.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print("✅ Saved results to aadhar_parsed.json")
    else:
        print("❌ Extraction failed.")


if __name__ == "__main__":
    main()