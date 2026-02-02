from fastapi import FastAPI
from app.schemas import AnalyzeRequest
from app.router import route_task

app = FastAPI(title="Universal AI API")

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    return route_task(
        sector=req.sector,
        task=req.task,
        input_data=req.input,
        options=req.options
    )
