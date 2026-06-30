import os
from dotenv import load_dotenv

load_dotenv()

# Server configurations
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8000

# Gemini default model settings
DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_TEMP = 0.7
DEFAULT_TOP_P = 0.95

def get_api_key(passed_key: str = None) -> str:
    """
    Securely resolve Gemini API key from parameters or environment.
    """
    key = (passed_key or "").strip()
    return key if key else os.getenv("GEMINI_API_KEY", "")
