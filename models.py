from pydantic import BaseModel
from typing import List, Optional

class GenerateRequest(BaseModel):
    objective: str
    persona_type: str
    techniques: List[str]
    formatting_style: str
    api_key: Optional[str] = None
    model_name: Optional[str] = "gemini-2.5-flash"

class TestRequest(BaseModel):
    assembled_prompt: str
    system_instruction: str
    temperature: float
    top_p: float
    api_key: Optional[str] = None
    model_name: Optional[str] = "gemini-2.5-flash"

class AnalyzeRequest(BaseModel):
    system_instruction: str
    template: str
