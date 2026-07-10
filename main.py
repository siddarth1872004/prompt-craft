import os
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Header, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import config
import client
import prompt_analyzer

app = FastAPI(
    title="PromptCraft API",
    description="FastAPI backend for prompt analysis, optimization, and security audits.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Schemas ───────────────────────────────────────────────────────────────────
class AnalyzeRequest(BaseModel):
    system_instruction: str
    template: str

class OptimizeRequest(BaseModel):
    objective: str
    persona_type: str
    techniques: List[str]
    formatting_style: str
    model_name: Optional[str] = "gemini-2.5-flash"

class TestRequest(BaseModel):
    assembled_prompt: str
    system_instruction: Optional[str] = ""
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.95
    model_name: Optional[str] = "gemini-2.5-flash"

# ── Endpoints ─────────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "PromptCraft API",
        "has_api_key": bool(config.get_api_key())
    }

@app.post("/api/analyze")
async def analyze_prompt_endpoint(req: AnalyzeRequest):
    try:
        analysis = prompt_analyzer.analyze_prompt(req.system_instruction, req.template)
        variables = prompt_analyzer.extract_variables([req.template])
        return {
            "analysis": analysis,
            "variables": variables
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prompt analysis failed: {str(e)}"
        )

@app.post("/api/optimize")
async def optimize_prompt_endpoint(req: OptimizeRequest, x_api_key: Optional[str] = Header(None)):
    api_key = x_api_key or config.get_api_key()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Gemini API Key is required. Set GEMINI_API_KEY environment variable or pass X-API-Key header."
        )
    try:
        result = client.generate_prompt_structure_with_gemini(
            api_key=api_key,
            model_name=req.model_name,
            objective=req.objective,
            persona_type=req.persona_type,
            techniques=req.techniques,
            formatting_style=req.formatting_style
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prompt optimization failed: {str(e)}"
        )

@app.post("/api/test")
async def test_prompt_endpoint(req: TestRequest, x_api_key: Optional[str] = Header(None)):
    api_key = x_api_key or config.get_api_key()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Gemini API Key is required. Set GEMINI_API_KEY environment variable or pass X-API-Key header."
        )
    try:
        response_text = client.test_prompt(
            api_key=api_key,
            model_name=req.model_name,
            assembled_prompt=req.assembled_prompt,
            system_instruction=req.system_instruction,
            temperature=req.temperature,
            top_p=req.top_p
        )
        return {"output": response_text}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prompt execution failed: {str(e)}"
        )
