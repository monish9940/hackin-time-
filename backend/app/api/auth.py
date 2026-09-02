import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional
from app.database import get_db
from app.db_helpers import clean_doc, get_next_sequence_value
from app.schemas import UserCreate, UserLogin, UserResponse, Token
from app.auth import verify_password, get_password_hash, create_access_token, get_current_user

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register(user_in: UserCreate, db = Depends(get_db)):
    if user_in.confirm_password and user_in.password != user_in.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
        
    existing_user = db.users.find_one({"email": user_in.email.lower()})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email is already registered")
        
    password_hash = get_password_hash(user_in.password)
    user_id = get_next_sequence_value(db, "users")
    
    user_doc = {
        "id": user_id,
        "full_name": user_in.full_name,
        "email": user_in.email.lower(),
        "password_hash": password_hash,
        "organization": user_in.organization or "General Hospital",
        "specialization": user_in.specialization or "General Physician",
        "role": (user_in.role or "clinician").lower(),
        "is_active": True,
        "created_at": datetime.datetime.utcnow().isoformat()
    }
    
    db.users.insert_one(user_doc)
    
    # Audit log
    db.audit_logs.insert_one({
        "id": get_next_sequence_value(db, "audit_logs"),
        "user_email": user_in.email.lower(),
        "action": "Register",
        "details": f"User account registered for {user_in.full_name}",
        "timestamp": datetime.datetime.utcnow().isoformat()
    })
    
    return clean_doc(user_doc)

from fastapi import Request

@router.post("/login", response_model=Token)
async def login(
    request: Request,
    db = Depends(get_db)
):
    email = None
    password = None
    
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            login_data = await request.json()
            email = login_data.get("email")
            password = login_data.get("password")
        except Exception:
            pass
    else:
        form = await request.form()
        email = form.get("username")
        password = form.get("password")
        
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")
        
    user_doc = db.users.find_one({"email": email.lower()})
    if not user_doc or not verify_password(password, user_doc.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = create_access_token(data={"sub": user_doc["email"]})
    
    # Audit log
    db.audit_logs.insert_one({
        "id": get_next_sequence_value(db, "audit_logs"),
        "user_email": user_doc["email"],
        "action": "Login",
        "details": f"User {user_doc['full_name']} logged into the system",
        "timestamp": datetime.datetime.utcnow().isoformat()
    })
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": clean_doc(user_doc)
    }

@router.get("/me", response_model=UserResponse)
def get_me(current_user: dict = Depends(get_current_user)):
    return current_user

@router.post("/logout")
def logout(current_user: dict = Depends(get_current_user), db = Depends(get_db)):
    db.audit_logs.insert_one({
        "id": get_next_sequence_value(db, "audit_logs"),
        "user_email": current_user["email"],
        "action": "Logout",
        "details": f"User {current_user['full_name']} logged out",
        "timestamp": datetime.datetime.utcnow().isoformat()
    })
    return {"message": "Successfully logged out"}

