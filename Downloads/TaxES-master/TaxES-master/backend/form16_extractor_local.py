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

FORM16_PROMPT = """You are a tax document parser. Extract ALL key-value pairs from this Form-16 document image.

Return a JSON array where each item has:
- "Key": the field label/name
- "Value": the corresponding value as a plain string
- "Confidence": a number between 0-100

Focus on extracting:
- Assessment Year, PAN, Employee Name, Address
- Salary components: 17(1), 17(2), 17(3), Gross Salary
- Section 10 exemptions
- Section 16 deductions: 16(ia), 16(ii), 16(iii)
- Income chargeable under salaries
- Deductions: 80C, 80CCC, 80CCD(1), 80CCD(1B), 80CCD(2), 80D, 80E, 80G, 80TTA
- Total deduction under section 80C, 80CCC and 80CCD(1)
- Tax on total income, Rebate 87A, Surcharge, Health and Education Cess
- Relief under section 89, Net tax payable

IMPORTANT: All values must be plain strings. Return ONLY a valid JSON array, no explanation text."""


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


def _to_float(value):
    if not value:
        return 0.0
    try:
        return float(re.sub(r'[^\d.]', '', str(value)))
    except Exception:
        return 0.0


def _parse_into_structured(pairs):
    """Map raw key-value pairs into the required structured output."""

    # Pick best value for a key: highest confidence, non-empty
    def best(keys):
        candidates = []
        for p in pairs:
            k = p['Key'].lower().strip()
            if any(kw in k for kw in keys) and p['Value'].strip():
                candidates.append(p)
        if not candidates:
            return ''
        return max(candidates, key=lambda x: x['Confidence'])['Value'].strip()

    salary_17_1 = _to_float(best(['17(1)']))
    salary_17_2 = _to_float(best(['17(2)']))
    salary_17_3 = _to_float(best(['17(3)']))
    gross = _to_float(best(['gross salary'])) or (salary_17_1 + salary_17_2 + salary_17_3)

    return {
        "assessment_year":              best(['assessment year']),
        "pan":                          best(['pan of the employee', 'pan']),
        "employee_address":             best(['name and address of the employee', 'address']),
        "gross_salary":                 gross,
        "salary_section_17_1":          salary_17_1,
        "prerequisites_section_17_2":   salary_17_2,
        "profits_section_17_3":         salary_17_3,
        "total_exemption_section_10":   _to_float(best(['section 10 exemption', 'total amount of exemption', 'section 10'])),
        "standard_deduction_16_ia":     _to_float(best(['16(ia)', '16(i)(a)'])),
        "entertainment_allowance_16_ii":_to_float(best(['16(ii)'])),
        "tax_on_employment_16_iii":     _to_float(best(['16(iii)'])),
        "income_chargeable_salaries":   _to_float(best(['income chargeable under the head', 'income chargeable under salaries'])),
        "gross_total_income":           _to_float(best(['gross total income'])) or _to_float(best(['income chargeable under the head', 'income chargeable under salaries'])),
        "deduction_80C":                _to_float(best(['80c'])),
        "deduction_80CCC":              _to_float(best(['80ccc'])),
        "deduction_80CCD1":             _to_float(best(['80ccd(1)', '80ccd (1)'])),
        "deduction_80CCD1B":            _to_float(best(['80ccd(1b)', '80ccd (1b)'])),
        "deduction_80CCD2":             _to_float(best(['80ccd(2)', '80ccd (2)'])),
        "deduction_80D":                _to_float(best(['80d'])),
        "deduction_80E":                _to_float(best(['80e'])),
        "deduction_80G":                _to_float(best(['80g'])),
        "deduction_80TTA":              _to_float(best(['80tta'])),
        "deduction_80C_total":          _to_float(best(['total deduction under section 80c', 'total deduction'])),
        "tax_on_total_income":          _to_float(best(['tax on total income'])),
        "rebate_87A":                   best(['87a', 'rebate']),
        "surcharge":                    _to_float(best(['surcharge'])),
        "health_education_cess":        _to_float(best(['health and education cess', 'education cess'])),
        "relief_section_89":            _to_float(best(['relief under section 89', 'section 89'])),
        "tax_payable":                  _to_float(best(['net tax payable', 'tax payable'])),
    }


class Form16ExtractorLocal:
    def extract_form16_data(self, pdf_path):
        try:
            doc = fitz.open(pdf_path)
            all_pairs = []

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                img_data = page.get_pixmap().tobytes("png")
                raw = _call_groq_vision(img_data, FORM16_PROMPT)
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
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else 'taxes_files/0a8ea44d-555a-40e5-9d34-a9da1e93b82d/uploads/form16.pdf'
    result = Form16ExtractorLocal().extract_form16_data(pdf_path)
    if result['status'] == 'success':
        print(json.dumps(result['parsed'], indent=2))
    else:
        print('Error:', result['message'])
