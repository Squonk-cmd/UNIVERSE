from pydantic import BaseModel
from typing import Dict, Any, Optional, Union

class AnalyzeRequest(BaseModel):
    sector: str
    task: str
    input: Union[str, Dict[str, Any]] # Can be text or a dict with {"text": "...", "image": "base64..."}
    options: Dict[str, Any] = {}