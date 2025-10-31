import requests
import os

def test_upload():
    """Test document upload endpoint"""
    try:
        # Create dummy PDF files for testing
        dummy_pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000074 00000 n \n0000000120 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n178\n%%EOF"
        
        # Write dummy files
        with open('test_aadhar.pdf', 'wb') as f:
            f.write(dummy_pdf_content)
        with open('test_bank.pdf', 'wb') as f:
            f.write(dummy_pdf_content)
        with open('test_form16.pdf', 'wb') as f:
            f.write(dummy_pdf_content)
        
        # Test upload
        files = {
            'aadhar': ('aadhar.pdf', open('test_aadhar.pdf', 'rb'), 'application/pdf'),
            'passbook': ('passbook.pdf', open('test_bank.pdf', 'rb'), 'application/pdf'),
            'form16': ('form16.pdf', open('test_form16.pdf', 'rb'), 'application/pdf')
        }
        
        data = {'user_id': 'test_user'}
        
        print("Testing document upload...")
        response = requests.post('http://localhost:8000/process-documents', files=files, data=data)
        
        # Close files
        for file_tuple in files.values():
            file_tuple[1].close()
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        # Clean up
        os.remove('test_aadhar.pdf')
        os.remove('test_bank.pdf')
        os.remove('test_form16.pdf')
        
    except Exception as e:
        print(f"Upload test failed: {e}")

if __name__ == "__main__":
    test_upload()