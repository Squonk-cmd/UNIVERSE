from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # <-- Import this
from pydantic import BaseModel
from typing import Optional
from app.models.ielts_evaluator import IELTSEvaluator

app = FastAPI()

# --- NEW CORS CONFIGURATION ---
# In production, replace ["*"] with your actual domain for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (localhost:3000, etc.)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (POST, GET, OPTIONS, etc.)
    allow_headers=["*"],  # Allows all headers
)

evaluator = IELTSEvaluator()

class FullTestRequest(BaseModel):
    task1_text: str
    task1_image: Optional[str] = None
    task2_text: str

@app.post("/analyze")
async def analyze_full_test(request: FullTestRequest):
    try:
        result = evaluator.evaluate_with_retry(
            task1_text=request.task1_text,
            task1_img_b64=request.task1_image,
            task2_text=request.task2_text
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["details"])
            
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")