import fitz, base64, requests, os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('GROQ_API_KEY')
url = "https://api.groq.com/openai/v1/chat/completions"
headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

doc = fitz.open("aadhar.pdf")
page = doc.load_page(0)
img_bytes = page.get_pixmap().tobytes("png")
img_b64 = base64.b64encode(img_bytes).decode('utf-8')
doc.close()

data = {
    "model": "meta-llama/llama-4-scout-17b-16e-instruct",
    "messages": [{"role": "user", "content": [
        {"type": "text", "text": "Extract all text from this Aadhar card image exactly as it appears. Include name, date of birth, gender, address, aadhar number. Return plain text only."},
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}}
    ]}],
    "temperature": 0.1,
    "max_tokens": 1024
}

r = requests.post(url, headers=headers, json=data, timeout=60)
print("Status:", r.status_code)
print("Raw Groq output:")
print(r.json()['choices'][0]['message']['content'])
