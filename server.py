import os
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Import our helper logic
import utils

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PromptCraftServer")

app = FastAPI(title="PromptCraft BFF API", description="Backend-For-Frontend server for PromptCraft Prompt Generator")

# Pydantic schemas for request validation
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

# API Endpoints
@app.post("/api/generate")
async def generate_prompt(req: GenerateRequest):
    api_key = req.api_key.strip() if req.api_key else os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        raise HTTPException(
            status_code=400, 
            detail="Gemini API Key is missing. Provide it in the request or configure it in the server environment."
        )
    
    if not req.objective.strip():
        raise HTTPException(
            status_code=400,
            detail="Objective is required to generate a prompt."
        )
    
    try:
        generated_data = utils.generate_prompt_structure_with_gemini(
            api_key=api_key,
            model_name=req.model_name,
            objective=req.objective,
            persona_type=req.persona_type,
            techniques=req.techniques,
            formatting_style=req.formatting_style
        )
        return generated_data
    except Exception as e:
        logger.error(f"Generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate prompt: {str(e)}")

@app.post("/api/test")
async def test_prompt_run(req: TestRequest):
    api_key = req.api_key.strip() if req.api_key else os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        raise HTTPException(
            status_code=400, 
            detail="Gemini API Key is missing. Provide it in the request or configure it in the server environment."
        )

    try:
        response_text = utils.test_prompt(
            api_key=api_key,
            model_name=req.model_name,
            assembled_prompt=req.assembled_prompt,
            system_instruction=req.system_instruction,
            temperature=req.temperature,
            top_p=req.top_p
        )
        return {"output": response_text}
    except Exception as e:
        logger.error(f"Execution error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")

@app.post("/api/analyze")
async def analyze_prompt_route(req: AnalyzeRequest):
    try:
        analysis_data = utils.analyze_prompt(
            system_instruction=req.system_instruction,
            template=req.template
        )
        return analysis_data
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# Mount static folder for frontend files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(
        content="<html><body><h3>PromptCraft: Static files not yet configured.</h3></body></html>",
        status_code=404
    )

if __name__ == "__main__":
    import uvicorn
    # Bind strictly to localhost (127.0.0.1) to avoid network exposure during development
    uvicorn.run(app, host="127.0.0.1", port=8000)
