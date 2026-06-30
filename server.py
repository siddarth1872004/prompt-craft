import os
import logging
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import config
from routes import router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PromptCraftServer")

app = FastAPI(title="PromptCraft BFF API", description="Modular Backend-For-Frontend server for PromptCraft")

# Allow local requestorigins for security validation
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Include BFF API endpoints
app.include_router(router)

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
    logger.info(f"Starting server process on http://{config.SERVER_HOST}:{config.SERVER_PORT}")
    uvicorn.run(app, host=config.SERVER_HOST, port=config.SERVER_PORT)
