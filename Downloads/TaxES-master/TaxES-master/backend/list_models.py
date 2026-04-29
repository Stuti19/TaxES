import requests, os
from dotenv import load_dotenv
load_dotenv()

key = os.getenv('GROQ_API_KEY')
r = requests.get('https://api.groq.com/openai/v1/models', headers={'Authorization': f'Bearer {key}'})
data = r.json()
for m in data.get('data', []):
    print(m['id'])
