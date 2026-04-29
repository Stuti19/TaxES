import fitz, base64, requests, os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('GROQ_API_KEY')
url = 'https://api.groq.com/openai/v1/chat/completions'
headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}

doc = fitz.open('aadhar.pdf')
print(f"Total pages: {len(doc)}")
for i, page in enumerate(doc):
    img_b64 = base64.b64encode(page.get_pixmap().tobytes('png')).decode()
    data = {
        'model': 'meta-llama/llama-4-scout-17b-16e-instruct',
        'messages': [{'role': 'user', 'content': [
            {'type': 'text', 'text': 'Read every single word and number visible in this image from top to bottom. Output exactly as seen, one item per line.'},
            {'type': 'image_url', 'image_url': {'url': f'data:image/png;base64,{img_b64}'}}
        ]}],
        'temperature': 0.1, 'max_tokens': 1024
    }
    r = requests.post(url, headers=headers, json=data, timeout=60)
    print(f"\n--- Page {i+1} ---")
    text = r.json()['choices'][0]['message']['content']
    print(text.encode('ascii', errors='replace').decode('ascii'))
doc.close()
