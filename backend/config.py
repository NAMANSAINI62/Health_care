import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgrespassword@localhost:5400/aivoa_complaints"
    )
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
    GROQ_MODEL_PRIMARY: str = os.getenv("GROQ_MODEL_PRIMARY", "qwen/qwen3.8-27b")
    GROQ_MODEL_CONTEXT: str = os.getenv("GROQ_MODEL_CONTEXT", "qwen/qwen3.8-27b")

settings = Settings()
