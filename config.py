import os
from dotenv import load_dotenv

class Config:
    load_dotenv()
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
