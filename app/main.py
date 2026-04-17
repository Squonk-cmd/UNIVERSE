from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # <-- Import this
from pydantic import BaseModel
from typing import Optional
import re  # <--- ADD THIS LINE HERE
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

# --- UTILITY FUNCTION FOR WORD COUNT ---
def get_clean_word_count(text: str) -> int:
    """
    Counts only words, ignoring punctuation, special characters, and extra spaces.
    Example: "Hello, world!" -> ['Hello', 'world'] -> Count: 2
    """
    if not text:
        return 0
    # This regex finds all alphanumeric sequences (words/numbers) 
    # and ignores punctuation like commas, periods, etc.
    words = re.findall(r'\b\w+\b', text)
    return len(words)

class FullTestRequest(BaseModel):
    task1_text: str
    task1_image: Optional[str] = None
    task2_text: str

@app.get("/")
async def root():
    return {"status": "ok"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}


_last_request_time = 0
_MIN_INTERVAL_SECONDS = 15  # enforce max ~4 requests/minute safely
@app.post("/analyze")
async def analyze_full_test(request: FullTestRequest):
    global _last_request_time
    now = time.time()
    elapsed = now - _last_request_time
    if elapsed < _MIN_INTERVAL_SECONDS:
        wait = round(_MIN_INTERVAL_SECONDS - elapsed)
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit: please wait {wait} more seconds before evaluating again."
        )
    _last_request_time = now
    try:
        # 1. Calculate word counts manually
        t1_count = get_clean_word_count(request.task1_text)
        t2_count = get_clean_word_count(request.task2_text)
        
        result = evaluator.evaluate_with_retry(
            task1_text=request.task1_text,
            task1_img_b64=request.task1_image,
            task1_word_count=t1_count,   # New parameter
            task2_text=request.task2_text,
            task2_word_count=t2_count    # New parameter
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["details"])
            
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")
