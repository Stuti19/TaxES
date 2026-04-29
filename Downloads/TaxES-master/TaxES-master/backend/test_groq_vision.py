import requests, os, base64, fitz
from dotenv import load_dotenv
load_dotenv()

key = os.getenv('GROQ_API_KEY')

# Get a small test image from the PDF
doc = fitz.open('taxes_files/0a8ea44d-555a-40e5-9d34-a9da1e93b82d/uploads/form16.pdf')
page = doc.load_page(0)
img_data = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5)).tobytes("png")  # smaller image
doc.close()

img_b64 = base64.b64encode(img_data).decode('utf-8')
print(f"Image size: {len(img_data)} bytes")

headers = {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}
data = {
    "model": "meta-llama/llama-4-scout-17b-16e-instruct",
    "messages": [{"role": "user", "content": [
        {"type": "text", "text": "What text do you see in this image? Return as JSON array of key-value pairs."},
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}}
    ]}],
    "temperature": 0.1,
    "max_tokens": 1024
}

r = requests.post('https://api.groq.com/openai/v1/chat/completions', headers=headers, json=data)
print("Status:", r.status_code)
print("Response:", r.text[:2000])
