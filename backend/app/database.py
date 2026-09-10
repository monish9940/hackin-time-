import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from app.config import settings

logger = logging.getLogger("carebridge")

client = None
db = None

def get_client():
    global client
    if client is None:
        if not settings.MONGODB_URI:
            raise RuntimeError("MONGODB_URI environment variable is required and must point to MongoDB Atlas.")
        client = MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=5000)
    return client

def get_db():
    global db
    if db is None:
        cli = get_client()
        db = cli[settings.MONGODB_DB_NAME]
    return db

def init_db():
    global db
    if not settings.MONGODB_URI:
        error_msg = "MongoDB Atlas connection failed: MONGODB_URI environment variable is not configured."
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    try:
        cli = get_client()
        cli.admin.command('ping')
        print("MongoDB Atlas connected successfully.")
        logger.info("MongoDB Atlas connected successfully.")
        
        db = cli[settings.MONGODB_DB_NAME]
        
        # Create required indexes
        db.users.create_index("email", unique=True)
        db.patients.create_index("patient_id", unique=True)
        db.documents.create_index("patient_id")
        db.timeline_events.create_index("patient_id")
        db.ai_insights.create_index("patient_id")
        db.doctor_notes.create_index("patient_id")
        db.audit_logs.create_index("user_email")
        
        print("MongoDB Atlas indexes created successfully.")
    except (ConnectionFailure, ServerSelectionTimeoutError, Exception) as e:
        error_type = type(e).__name__
        error_msg = f"MongoDB Atlas connection failed ({error_type}). Please verify MONGODB_URI environment variable and network access."
        print(error_msg)
        logger.error(error_msg)
        raise RuntimeError(error_msg)


