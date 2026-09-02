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
    MONGODB_URI: str = os.getenv("MONGODB_URI") or os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "carebridge_db")
    
    # JWT Authentication Settings
    JWT_SECRET: str = os.getenv("JWT_SECRET") or os.getenv("SECRET_KEY", "carebridge_jwt_secret_key_super_secure_random_2026")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM") or os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    
    # LLM Settings
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
    
    UPLOAD_DIR: str = os.path.join(base_dir, "uploads")

settings = Settings()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
