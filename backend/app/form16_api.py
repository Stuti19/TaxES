from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from form16_extractor import extract_form16

router = APIRouter()

class Form16Request(BaseModel):
    user_id: str

@router.post("/extract-form16")
async def extract_form16_data(request: Form16Request):
    try:
        result = extract_form16(request.user_id)
        
        if result['status'] == 'error':
            raise HTTPException(status_code=400, detail=result['message'])
        
        return {
            "message": "Form 16 data extracted successfully",
            "extracted_pairs_count": result['extracted_pairs_count'],
            "csv_file": result['csv_file'],
            "key_value_pairs": result['data']
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))