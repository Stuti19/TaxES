#!/usr/bin/env python3
"""
Production server startup script for TaxES
Optimized for document processing without debug mode
"""

import os
import sys
from pathlib import Path

def setup_environment():
    """Setup optimized environment for production"""
    # Disable PyTorch warnings
    os.environ['PYTHONWARNINGS'] = 'ignore'
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    
    # EasyOCR optimizations
    os.environ['EASYOCR_MODULE_PATH'] = os.path.expanduser('~/.EasyOCR')
    os.environ['TORCH_HOME'] = os.path.expanduser('~/.torch')
    
    # Flask optimizations
    os.environ['FLASK_ENV'] = 'production'
    os.environ['WERKZEUG_RUN_MAIN'] = 'true'

def create_directories():
    """Create necessary directories"""
    directories = [
        'taxes_files',
        'taxes_files/uploads',
        'taxes_files/extracted_data',
        'taxes_files/parsed',
        'taxes_files/excel'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("Created necessary directories")

def main():
    """Start production server"""
    print("Starting TaxES Production Server...")
    
    setup_environment()
    create_directories()
    
    print("Environment optimized for production")
    print("Starting Flask server on http://localhost:8000")
    
    # Import and run server
    from server import app
    app.run(
        debug=False,
        host='0.0.0.0',
        port=8000,
        threaded=True,
        use_reloader=False
    )

if __name__ == '__main__':
    main()