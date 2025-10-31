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
            prompt = f"""
Parse this Indian address carefully. The address may contain a person's name at the beginning which should be ignored.

Address: {address}

Extract these components and return JSON:
- flat_door_block_no: Only the flat/door/house number (like "15", "A-101", "23B")
- premises_building_village: Building/colony/village name (like "Ashok Nagar", "Green Park")
- road_street_post_office: Road/street name
- area_locality: Area/locality name
- town_city_district: Valid Indian city/district name only
- state: Valid Indian state name only
- pin_code: 6-digit PIN code if found

Example:
Address: "DIO Mukesh Kumar H, 15 Ashok Nagar Shahdara Mandoli, Saboli North East Delhi, 110093"
Should return:
{{
  "flat_door_block_no": "15",
  "premises_building_village": "Ashok Nagar",
  "road_street_post_office": "Shahdara Mandoli",
  "area_locality": "Saboli",
  "town_city_district": "Delhi",
  "state": "Delhi",
  "pin_code": "110093"
}}

IMPORTANT:
- Ignore person names at the beginning
- Extract only numbers for flat_door_block_no
- Use only REAL Indian state names
- If unsure about state/city, leave empty

Return only valid JSON:
"""
            
            response = self._call_groq_api(prompt)
            parsed = json.loads(response)
            
            # Validate and clean the response
            return self._validate_address_components(parsed)
        except Exception as e:
            print(f"Address parsing error: {e}")
            # Fallback to simple parsing
            return self._fallback_address_parse(address)
    
    def _call_groq_api(self, prompt):
        """Make API call to Groq"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "llama3-8b-8192",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 200
        }
        
        response = requests.post(self.base_url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    
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
            'west bengal', 'delhi', 'chandigarh', 'dadra and nagar haveli',
            'daman and diu', 'lakshadweep', 'puducherry', 'andaman and nicobar islands',
            'jammu and kashmir', 'ladakh', 'mp', 'up', 'hp'
        }
        
        # Clean state field
        state = parsed.get('state', '').lower().strip()
        if state not in indian_states:
            parsed['state'] = ''
        
        # Validate PIN code
        pin_code = parsed.get('pin_code', '')
        if not pin_code or not pin_code.isdigit() or len(pin_code) != 6:
            parsed['pin_code'] = ''
        
        # Ensure flat_door_block_no exists
        if 'flat_door_block_no' not in parsed:
            parsed['flat_door_block_no'] = ''
        
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