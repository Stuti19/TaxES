import requests
import json

def test_server():
    """Test if server is responding"""
    try:
        # Test health endpoint
        response = requests.get('http://localhost:8000/health')
        print(f"Health check: {response.status_code} - {response.json()}")
        
        # Test basic endpoint
        response = requests.get('http://localhost:8000/test')
        print(f"Test endpoint: {response.status_code} - {response.json()}")
        
        return True
    except Exception as e:
        print(f"Server test failed: {e}")
        return False

if __name__ == "__main__":
    test_server()