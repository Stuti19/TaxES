import os
import json
import base64
import re
import requests
import fitz
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

PASSBOOK_PROMPT = """You are a bank document parser. Extract ALL key-value pairs from this bank passbook document image.

Return a JSON array where each item has:
- "Key": the field label/name
- "Value": the corresponding value as a plain string
- "Confidence": a number between 0-100

Focus on extracting:
- Account Holder Name / Customer Name
- Account Number
- IFSC Code
- Bank Name
- Branch Name
- Any header text lines (use "Header Text" as Key)

IMPORTANT: All values must be plain strings. Return ONLY a valid JSON array, no explanation text."""

IFSC_TO_BANK = {
    'SBIN': 'State Bank of India', 'PUNB': 'Punjab National Bank',
    'BARB': 'Bank of Baroda', 'CNRB': 'Canara Bank',
    'BKID': 'Bank of India', 'UBIN': 'Union Bank of India',
    'MAHB': 'Bank of Maharashtra', 'IDIB': 'Indian Bank',
    'CBIN': 'Central Bank of India', 'IOBA': 'Indian Overseas Bank',
    'UCBA': 'UCO Bank', 'PSIB': 'Punjab & Sind Bank',
    'HDFC': 'HDFC Bank', 'ICIC': 'ICICI Bank',
    'KKBK': 'Kotak Mahindra Bank', 'UTIB': 'Axis Bank',
    'INDB': 'IndusInd Bank', 'FDRL': 'Federal Bank', 'YESB': 'Yes Bank'
}


def _image_to_base64(img_bytes):
    return base64.b64encode(img_bytes).decode('utf-8')


def _call_groq_vision(img_bytes, prompt):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": VISION_MODEL,
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{_image_to_base64(img_bytes)}"}}
        ]}],
        "temperature": 0.1,
        "max_tokens": 4096
    }
    for attempt in range(5):
        response = requests.post(GROQ_URL, headers=headers, json=data, timeout=60)
        if response.status_code == 429:
            wait = int(response.headers.get('retry-after', 60))
            print(f"Rate limited. Waiting {wait}s before retry ({attempt+1}/5)...")
            import time; time.sleep(wait)
            continue
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()
    raise Exception("Groq rate limit exceeded after 5 retries")


def _flatten_value(value):
    if isinstance(value, dict):
        return ', '.join(f"{k}: {v}" for k, v in value.items())
    return str(value)


def _parse_groq_response(raw_text):
    start = raw_text.find('[')
    end = raw_text.rfind(']') + 1
    if start == -1 or end == 0:
        return []
    try:
        items = json.loads(raw_text[start:end])
        normalized = []
        for item in items:
            if isinstance(item, dict):
                key = item.get('Key') or item.get('key', '')
                value = item.get('Value') or item.get('value', '')
                confidence = item.get('Confidence') or item.get('confidence', 85)
                normalized.append({
                    'Key': str(key),
                    'Value': _flatten_value(value),
                    'Confidence': confidence
                })
        return normalized
    except json.JSONDecodeError:
        return []


def _parse_into_structured(pairs):
    def best(keys):
        candidates = []
        for p in pairs:
            k = p['Key'].lower().strip()
            if any(kw in k for kw in keys) and p['Value'].strip():
                candidates.append(p)
        if not candidates:
            return ''
        return max(candidates, key=lambda x: x['Confidence'])['Value'].strip()

    name = best(['account holder name', 'customer name', 'holder name']) or best(['name'])
    account_number = best(['account number', 'account no', 'a/c no'])
    ifsc = best(['ifsc code', 'ifsc'])

    # Clean account number — digits only
    acc_match = re.search(r'\d{9,18}', account_number)
    account_number = acc_match.group() if acc_match else account_number

    # Clean IFSC
    ifsc_match = re.search(r'[A-Z]{4}0[A-Z0-9]{6}', ifsc.upper())
    ifsc = ifsc_match.group() if ifsc_match else ifsc.upper()

    # Derive bank name from IFSC prefix first, fallback to extracted
    bank_name = IFSC_TO_BANK.get(ifsc[:4], '') if len(ifsc) >= 4 else ''
    if not bank_name:
        bank_name = best(['bank name', 'bank'])

    return {
        "name": name,
        "accountNumber": account_number,
        "bankName": bank_name,
        "IFSC_Code": ifsc
    }


class PassbookExtractorLocal:
    def extract_passbook_data(self, pdf_path):
        try:
            doc = fitz.open(pdf_path)
            all_pairs = []

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                img_data = page.get_pixmap().tobytes("png")
                raw = _call_groq_vision(img_data, PASSBOOK_PROMPT)
                all_pairs.extend(_parse_groq_response(raw))

            doc.close()

            structured = _parse_into_structured(all_pairs)

            return {
                'status': 'success',
                'extracted_pairs_count': len(all_pairs),
                'data': all_pairs,
                'parsed': structured
            }

        except Exception as e:
            return {'status': 'error', 'message': str(e)}


if __name__ == '__main__':
    import sys
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else 'taxes_files/0a8ea44d-555a-40e5-9d34-a9da1e93b82d/uploads/bank.pdf'
    result = PassbookExtractorLocal().extract_passbook_data(pdf_path)
    if result['status'] == 'success':
        print(json.dumps(result['parsed'], indent=2))
    else:
        print('Error:', result['message'])
