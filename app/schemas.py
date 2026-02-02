from pydantic import BaseModel
from typing import Dict, Any

class AnalyzeRequest(BaseModel):
    sector: str
    task: str
    input: Any
    options: Dict[str, Any] = {}
