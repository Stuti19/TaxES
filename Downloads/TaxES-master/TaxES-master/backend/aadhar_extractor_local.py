import re
import os
import json
from pathlib import Path

class AadharExtractorLocal:
    def __init__(self):
        self.extracted_data = {
            'aadhar_number': None,
            'name': None,
            'dob': None,
            'gender': None,
            'address': None,
            'raw_text': ''
        }
        self.ocr_reader = None

    def get_ocr_reader(self):
        """Initialize EasyOCR reader with optimizations"""
        if self.ocr_reader is None:
            try:
                import easyocr
                import os
                os.environ['EASYOCR_MODULE_PATH'] = os.path.expanduser('~/.EasyOCR')
                self.ocr_reader = easyocr.Reader(['en'], gpu=False, verbose=False, download_enabled=False)
            except ImportError:
                print("EasyOCR not installed. Please install: pip install easyocr")
                return None
            except Exception as e:
                print(f"EasyOCR initialization error: {e}")
                return None
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

    def extract_aadhar_number(self, text):
        """Extract 12-digit aadhar number"""
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
        lines = [self.clean_text_line(l) for l in text.split('\n') if l.strip()]
        
        address_lines = []
        found_address_keyword = False
        
        for i, line in enumerate(lines):
            line_upper = line.upper()
            
            if re.search(r'\bADDRESS\b', line_upper) and len(line) < 30:
                found_address_keyword = True
                if ':' in line:
                    after_colon = line.split(':', 1)[1].strip()
                    if len(after_colon) > 3:
                        address_lines.append(after_colon)
                continue
            
            if found_address_keyword:
                if len(line) < 3:
                    continue
                
                if re.search(r'\d{4}\s?\d{4}\s?\d{4}', line):
                    continue
                
                if any(keyword in line_upper for keyword in ['GOVERNMENT', 'UIDAI', 'UNIQUE', 'ISSUED']):
                    continue
                
                is_address_line = any([
                    re.search(r'\b\d{6}\b', line),
                    any(w in line_upper for w in ['S/O', 'C/O', 'D/O', 'W/O']),
                    any(w in line_upper for w in ['DIST', 'DISTRICT', 'STATE', 'VILLAGE', 'CITY', 'TOWN']),
                    ',' in line,
                    re.search(r'\b(ROAD|STREET|LANE|COLONY|NAGAR|GANJ|PUR)\b', line_upper),
                    len(line) > 10
                ])
                
                if is_address_line:
                    address_lines.append(line)
                    
                if len(address_lines) >= 5:
                    break
                    
                if any(keyword in line_upper for keyword in ['ENROLLMENT', 'DOWNLOAD', 'HELP']):
                    break
        
        if not address_lines:
            for i, line in enumerate(lines):
                if re.search(r'\b\d{6}\b', line):
                    start = max(0, i - 3)
                    for j in range(start, min(i + 2, len(lines))):
                        clean_line = lines[j]
                        if (len(clean_line) > 5 and 
                            not re.search(r'\d{4}\s?\d{4}\s?\d{4}', clean_line) and
                            not any(k in clean_line.upper() for k in ['GOVERNMENT', 'UIDAI'])):
                            address_lines.append(clean_line)
                    if address_lines:
                        break
        
        if address_lines:
            seen = set()
            unique_lines = []
            for line in address_lines:
                if line not in seen:
                    seen.add(line)
                    unique_lines.append(line)
            
            return ', '.join(unique_lines)
        
        return None

    def process_pdf(self, pdf_path):
        """Try to extract text directly, fallback to Groq vision OCR"""
        try:
            import fitz
            text = ''
            with fitz.open(pdf_path) as doc:
                for page in doc:
                    text += page.get_text() + "\n"
            
            if len(text.strip()) > 50:
                return text
            
            # Fallback to Groq vision
            print("Text extraction failed, using Groq vision OCR...")
            return self._groq_ocr(pdf_path)
        except Exception as e:
            return f"Error processing PDF: {str(e)}"

    def _groq_ocr(self, pdf_path):
        """Use Groq vision to extract structured aadhar data directly"""
        import fitz, base64, requests, time
        from dotenv import load_dotenv
        load_dotenv()

        api_key = os.getenv('GROQ_API_KEY')
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        prompt = """This is a page from an Indian Aadhar card. Extract the following and return ONLY valid JSON:
{
  "name": "the person's own name (single word or full name, appears before DOB line, NOT father's name which starts with D/O or S/O)",
  "dob": "date of birth in dd/mm/yyyy format (look for DOB: label)",
  "gender": "Male or Female (look for MALE or FEMALE text)",
  "aadhar_number": "12 digit number formatted as XXXX XXXX XXXX (ignore VID number)",
  "address": "full address text after the word Address (ignore Hindi text, only English address)"
}
If a field is not visible on this page, set it to null. Return only JSON."""

        full_text = ''
        doc = fitz.open(pdf_path)
        for page in doc:
            img_bytes = page.get_pixmap().tobytes("png")
            img_b64 = base64.b64encode(img_bytes).decode('utf-8')
            data = {
                "model": "meta-llama/llama-4-scout-17b-16e-instruct",
                "messages": [{"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}}
                ]}],
                "temperature": 0.1,
                "max_tokens": 1024
            }
            for attempt in range(5):
                r = requests.post(url, headers=headers, json=data, timeout=60)
                if r.status_code == 429:
                    wait = int(r.headers.get('retry-after', 60))
                    print(f"Rate limited. Waiting {wait}s before retry ({attempt+1}/5)...")
                    time.sleep(wait)
                    continue
                r.raise_for_status()
                full_text += r.json()['choices'][0]['message']['content'].strip() + "\n"
                break
        doc.close()
        return full_text

    def _parse_groq_json(self, text):
        """Parse JSON from all pages and merge into extracted_data"""
        import json
        # Find all JSON objects in the text (one per page)
        filled = False
        start = 0
        while True:
            s = text.find('{', start)
            e = text.find('}', s) + 1
            if s == -1 or e == 0:
                break
            # Find the last closing brace for this object
            depth = 0
            for idx in range(s, len(text)):
                if text[idx] == '{': depth += 1
                elif text[idx] == '}':
                    depth -= 1
                    if depth == 0:
                        e = idx + 1
                        break
            try:
                data = json.loads(text[s:e])
                # Merge: only overwrite if current value is None
                for key in ['name', 'dob', 'gender', 'aadhar_number', 'address']:
                    val = data.get(key)
                    if val and val != 'null' and not self.extracted_data.get(key):
                        self.extracted_data[key] = val
                filled = True
            except Exception:
                pass
            start = e
        return filled

    def extract_aadhar_data(self, pdf_path):
        """Extract all aadhar fields from PDF"""
        try:
            import fitz
            # Try direct text extraction first
            text = ''
            with fitz.open(pdf_path) as doc:
                for page in doc:
                    text += page.get_text() + "\n"

            if len(text.strip()) > 50:
                # Digital PDF — use regex extractors
                self.extracted_data['raw_text'] = text
                self.extracted_data['aadhar_number'] = self.extract_aadhar_number(text)
                self.extracted_data['dob'] = self.extract_dob(text)
                self.extracted_data['name'] = self.extract_name(text)
                self.extracted_data['gender'] = self.extract_gender(text)
                self.extracted_data['address'] = self.extract_address(text)
            else:
                # Scanned PDF — use Groq vision
                groq_text = self._groq_ocr(pdf_path)
                if not self._parse_groq_json(groq_text):
                    # Fallback: try regex on Groq plain text
                    self.extracted_data['aadhar_number'] = self.extract_aadhar_number(groq_text)
                    self.extracted_data['dob'] = self.extract_dob(groq_text)
                    self.extracted_data['name'] = self.extract_name(groq_text)
                    self.extracted_data['gender'] = self.extract_gender(groq_text)
                    self.extracted_data['address'] = self.extract_address(groq_text)

            output_data = {k: v for k, v in self.extracted_data.items() if k != 'raw_text'}
            return {'status': 'success', 'data': output_data}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}