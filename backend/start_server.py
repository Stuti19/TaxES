#!/usr/bin/env python3
"""
Startup script for the document processing server
"""
import os
import sys
from pathlib import Path

def check_requirements():
    """Check if all required packages are installed"""
    required_packages = [
        'flask', 'flask_cors', 'boto3', 'dotenv', 
        'fitz', 'PIL', 'easyocr'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"Missing packages: {', '.join(missing)}")
        print("Please install requirements: pip install -r requirements.txt")
        return False
    return True

def check_env_file():
    """Check if .env file exists"""
    env_file = Path('.env')
    if not env_file.exists():
        print("Warning: .env file not found!")
        print("Please copy .env.example to .env and fill in your AWS credentials")
        return False
    return True

def create_directories():
    """Create necessary directories"""
    directories = [
        'taxes_files/uploads',
        'taxes_files/extracted_data', 
        'taxes_files/parsed'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("Created necessary directories")

def main():
    print("Starting TaxES Document Processing Server...")
    
    if not check_requirements():
        sys.exit(1)
    
    if not check_env_file():
        print("Continuing without .env file (some features may not work)")
    
    create_directories()
    
    print("All checks passed. Starting Flask server...")
    
    # Import and run the Flask app
    from server import app
    app.run(debug=True, host='0.0.0.0', port=8000)

if __name__ == '__main__':
    main()