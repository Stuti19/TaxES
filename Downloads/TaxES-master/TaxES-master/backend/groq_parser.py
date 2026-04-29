import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

class GroqParser:
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY', 'gsk_your_api_key_here')
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        
    def parse_name(self, full_name):
        """Parse full name into first, middle, last name using Groq API"""
        try:
            prompt = f"""
Parse this name into first name, middle name, and last name.
Return only a JSON object with keys: first_name, middle_name, last_name
If there's no middle name, set it to empty string.

Name: {full_name}

Example response:
{{"first_name": "John", "middle_name": "Kumar", "last_name": "Sharma"}}
"""
            
            response = self._call_groq_api(prompt)
            return json.loads(response)
        except Exception as e:
            print(f"Name parsing error: {e}")
            # Fallback to simple parsing
            return self._fallback_name_parse(full_name)
    
    def parse_address(self, address):
        """Parse address into components using Groq API"""
        try:
            prompt = f"""You are an expert at parsing Indian addresses.

Parse this address into components. Return ONLY a valid JSON object, no explanation.

Address: {address}

Indian States and UTs (use EXACT names from this list):
Andhra Pradesh, Arunachal Pradesh, Assam, Bihar, Chhattisgarh, Goa, Gujarat,
Haryana, Himachal Pradesh, Jharkhand, Karnataka, Kerala, Madhya Pradesh,
Maharashtra, Manipur, Meghalaya, Mizoram, Nagaland, Odisha, Punjab, Rajasthan,
Sikkim, Tamil Nadu, Telangana, Tripura, Uttar Pradesh, Uttarakhand, West Bengal,
Andaman and Nicobar Islands, Chandigarh, Dadra and Nagar Haveli and Daman and Diu,
Delhi, Jammu and Kashmir, Ladakh, Lakshadweep, Puducherry

Rules:
- flat_door_block_no: house/flat/door number only (e.g. "E-376", "15", "A-101")
- premises_building_village: colony/society/village name
- road_street_post_office: street/road/post office name
- area_locality: area or locality name
- town_city_district: city or district name
- state: MUST be one of the exact state names listed above. Match by PIN code range or city name if needed.
- pin_code: 6-digit PIN code only

PIN code to state hints:
- 110xxx = Delhi
- 400xxx = Maharashtra
- 560xxx = Karnataka
- 600xxx = Tamil Nadu
- 700xxx = West Bengal
- 500xxx = Telangana
- 380xxx-396xxx = Gujarat
- 302xxx-342xxx = Rajasthan
- 201xxx-285xxx = Uttar Pradesh
- 800xxx-855xxx = Bihar
- 226xxx = Uttar Pradesh
- 160xxx = Chandigarh
- 180xxx-194xxx = Jammu and Kashmir

Return JSON:
{{
  "flat_door_block_no": "",
  "premises_building_village": "",
  "road_street_post_office": "",
  "area_locality": "",
  "town_city_district": "",
  "state": "",
  "pin_code": ""
}}"""

            response = self._call_groq_api(prompt)
            # Extract JSON from response
            start = response.find('{')
            end = response.rfind('}') + 1
            parsed = json.loads(response[start:end])
            return self._validate_address_components(parsed)
        except Exception as e:
            print(f"Address parsing error: {e}")
            return self._fallback_address_parse(address)
    
    def _call_groq_api(self, prompt):
        """Make API call to Groq"""
        import time
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            # "model": "llama3-8b-8192",
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 500
        }
        
        for attempt in range(5):
            response = requests.post(self.base_url, headers=headers, json=data)
            if response.status_code == 429:
                wait = int(response.headers.get('retry-after', 30))
                print(f"Rate limited. Waiting {wait}s before retry ({attempt+1}/5)...")
                time.sleep(wait)
                continue
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content'].strip()
        raise Exception("Groq rate limit exceeded after 5 retries")
    
    def _fallback_name_parse(self, full_name):
        """Fallback name parsing without API"""
        if not full_name or full_name.lower() == "no":
            return {"first_name": "", "middle_name": "", "last_name": ""}
        
        parts = full_name.strip().split()
        if len(parts) == 1:
            return {"first_name": parts[0], "middle_name": "", "last_name": ""}
        elif len(parts) == 2:
            return {"first_name": parts[0], "middle_name": "", "last_name": parts[1]}
        else:
            return {"first_name": parts[0], "middle_name": " ".join(parts[1:-1]), "last_name": parts[-1]}
    
    def _validate_address_components(self, parsed):
        """Validate and clean address components"""
        indian_states = {
            'andhra pradesh', 'arunachal pradesh', 'assam', 'bihar', 'chhattisgarh',
            'goa', 'gujarat', 'haryana', 'himachal pradesh', 'jharkhand', 'karnataka',
            'kerala', 'madhya pradesh', 'maharashtra', 'manipur', 'meghalaya',
            'mizoram', 'nagaland', 'odisha', 'punjab', 'rajasthan', 'sikkim',
            'tamil nadu', 'telangana', 'tripura', 'uttar pradesh', 'uttarakhand',
            'west bengal', 'andaman and nicobar islands', 'chandigarh',
            'dadra and nagar haveli and daman and diu', 'delhi', 'jammu and kashmir',
            'ladakh', 'lakshadweep', 'puducherry'
        }

        state = parsed.get('state', '').strip()
        if state.lower() not in indian_states:
            parsed['state'] = ''
        
        pin_code = str(parsed.get('pin_code', '')).strip()
        if not pin_code.isdigit() or len(pin_code) != 6:
            parsed['pin_code'] = ''
        
        for key in ['flat_door_block_no', 'premises_building_village', 'road_street_post_office',
                    'area_locality', 'town_city_district', 'state', 'pin_code']:
            if key not in parsed:
                parsed[key] = ''

        return parsed
    
    def _fallback_address_parse(self, address):
        """Fallback address parsing without API"""
        import re
        
        # Extract PIN code
        pin_match = re.search(r'\b\d{6}\b', address)
        pin_code = pin_match.group() if pin_match else ""
        
        # Extract flat/door/block number (look for standalone numbers)
        flat_match = re.search(r'\b\d+[A-Z]?\b', address)
        flat_no = flat_match.group() if flat_match else ""
        
        # Simple address splitting
        parts = [part.strip() for part in address.split(',') if part.strip()]
        
        return {
            "flat_door_block_no": flat_no,
            "premises_building_village": parts[1] if len(parts) > 1 else "",
            "road_street_post_office": parts[2] if len(parts) > 2 else "",
            "area_locality": parts[3] if len(parts) > 3 else "",
            "town_city_district": "",  # Leave empty for invalid data
            "state": "",  # Leave empty for invalid data
            "pin_code": pin_code
        }

def test_parser():
    """Test the parser with sample data"""
    parser = GroqParser()
    
    # Test name parsing
    name_result = parser.parse_name("Anjali")
    print("Name parsing result:", name_result)
    
    # Test address parsing with the corrected address
    address_result = parser.parse_address("DIO Mukesh Kumar H, 15 Ashok Nagar Shahdara Mandoli, Saboli North East Delhi, 110093, help uldal gov In")
    print("Address parsing result:", address_result)

if __name__ == "__main__":
    test_parser()