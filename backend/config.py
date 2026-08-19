import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgrespassword@localhost:5400/aivoa_complaints"
    )
    GROQ_MODEL_PRIMARY: str = os.getenv("GROQ_MODEL_PRIMARY", "llama-3.3-70b-versatile")
    GROQ_MODEL_CONTEXT: str = os.getenv("GROQ_MODEL_CONTEXT", "llama-3.3-70b-versatile")

settings = Settings()
