import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    HF_API_KEY: str = os.getenv("HF_API_KEY", "")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgrespassword@localhost:5400/aivoa_complaints"
    )
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
    HF_MODEL_PRIMARY: str = os.getenv("HF_MODEL_PRIMARY", "Qwen/Qwen2.5-Coder-32B-Instruct")
    GROQ_MODEL_PRIMARY: str = os.getenv("GROQ_MODEL_PRIMARY", "qwen/qwen3.8-27b")
    GROQ_MODEL_CONTEXT: str = os.getenv("GROQ_MODEL_CONTEXT", "llama-3.3-70b-versatile")

settings = Settings()
