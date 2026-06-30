import logging
from fastapi import APIRouter, HTTPException
import config
from models import GenerateRequest, TestRequest, AnalyzeRequest
import client
import prompt_analyzer

logger = logging.getLogger("PromptCraftRoutes")
router = APIRouter()

@router.post("/api/generate")
async def generate_prompt(req: GenerateRequest):
    api_key = config.get_api_key(req.api_key)
    if not api_key:
        raise HTTPException(
            status_code=400, 
            detail="Gemini API Key is missing. Provide it in the request or configure it in the server environment."
        )
    
    try:
        generated_data = client.generate_prompt_structure_with_gemini(
            api_key=api_key,
            model_name=req.model_name or config.DEFAULT_MODEL,
            objective=req.objective,
            persona_type=req.persona_type,
            techniques=req.techniques,
            formatting_style=req.formatting_style
        )
        return generated_data
    except Exception as e:
        logger.error(f"Generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate prompt: {str(e)}")

@router.post("/api/test")
async def test_prompt_run(req: TestRequest):
    api_key = config.get_api_key(req.api_key)
    if not api_key:
        raise HTTPException(
            status_code=400, 
            detail="Gemini API Key is missing. Provide it in the request or configure it in the server environment."
        )

    try:
        response_text = client.test_prompt(
            api_key=api_key,
            model_name=req.model_name or config.DEFAULT_MODEL,
            assembled_prompt=req.assembled_prompt,
            system_instruction=req.system_instruction,
            temperature=req.temperature,
            top_p=req.top_p
        )
        return {"output": response_text}
    except Exception as e:
        logger.error(f"Execution error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")

@router.post("/api/analyze")
async def analyze_prompt_route(req: AnalyzeRequest):
    try:
        analysis_data = prompt_analyzer.analyze_prompt(
            system_instruction=req.system_instruction,
            template=req.template
        )
        return analysis_data
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
