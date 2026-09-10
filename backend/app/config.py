import os
from dotenv import load_dotenv

# Load environment variables from .env file
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(base_dir, ".env"))

class Settings:
    PROJECT_NAME: str = "CareBridge AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # MongoDB Atlas Settings
    MONGODB_URI: str = os.getenv("MONGODB_URI") or os.getenv("MONGODB_URL", "")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "carebridge_db")
    
    # JWT Authentication Settings
    JWT_SECRET: str = os.getenv("JWT_SECRET") or os.getenv("SECRET_KEY", "carebridge_jwt_secret_key_super_secure_random_2026")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM") or os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    
    # CORS Origins
    _default_cors = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://hackin-time-w27p.vercel.app",
    ]
    _raw_cors: str = os.getenv("CORS_ORIGINS", "")
    _parsed_cors = [origin.strip() for origin in _raw_cors.split(",") if origin.strip()]
    CORS_ORIGINS: list = list(dict.fromkeys(_parsed_cors + _default_cors))

    # LLM Settings
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
    
    # OCR Tesseract Settings
    TESSERACT_CMD: str = os.getenv("TESSERACT_CMD", "")

    # Storage Settings
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "/tmp/uploads" if os.name != "nt" else os.path.join(base_dir, "uploads"))

settings = Settings()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

