#!/usr/bin/env python3
import uvicorn
import sys
import os

def start_server():
    """Start the FastAPI server with proper configuration"""
    try:
        print("Starting TaxES Backend Server...")
        print("Server will be available at: http://localhost:8000")
        print("Health check: http://localhost:8000/health")
        print("API docs: http://localhost:8000/docs")
        print("\nPress Ctrl+C to stop the server")
        
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_server()