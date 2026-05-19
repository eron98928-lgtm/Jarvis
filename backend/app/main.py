from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
import logging
import os

from .core import models, security, database
from .core.security_config import security_settings
from .core.middleware import SecurityMiddleware, IPBlockingMiddleware, audit_logger, DefenseMiddleware
from .modules.assistant import AssistantModule
from .modules.finance import FinanceModule
from .core.context_manager import ContextManager

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Initialize Rate Limiter
limiter = Limiter(key_func=get_remote_address)

# Database initialization
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="JARVIS API - Secure Edition")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 1. CORS Restriction
app.add_middleware(
    CORSMiddleware,
    allow_origins=security_settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# 2. Custom Security Middlewares
app.add_middleware(SecurityMiddleware)
app.add_middleware(IPBlockingMiddleware)
app.add_middleware(DefenseMiddleware)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- Pydantic Models for Strict Validation ---
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    
    @validator('message')
    def sanitize_message(cls, v):
        return security.sanitize_input(v)

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

# --- Dependencies ---
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = security.decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username: str = payload.get("sub")
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# --- Routes ---

@app.post("/token", response_model=TokenResponse)
@limiter.limit(security_settings.AUTH_RATE_LIMIT)
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        audit_logger.warning(f"Failed login attempt for user: {form_data.username} from IP: {request.client.host}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = security.create_access_token(data={"sub": user.username, "level": user.access_level})
    refresh_token = security.create_refresh_token(data={"sub": user.username})
    
    audit_logger.info(f"User logged in: {user.username}")
    return {
        "access_token": access_token, 
        "refresh_token": refresh_token, 
        "token_type": "bearer"
    }

assistant = AssistantModule()
finance = FinanceModule()

@app.post("/chat")
@limiter.limit(security_settings.DEFAULT_RATE_LIMIT)
async def chat(request: Request, chat_data: ChatRequest, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    ctx_mgr = ContextManager(db)
    context = ctx_mgr.get_active_context(user.id)
    
    response = await assistant.chat(chat_data.message, user.access_level, context, db, user.id)
    
    # Encrypt sensitive interactions before storing if needed
    # For now, we store as is but the capability is in security.py
    ctx_mgr.add_interaction(user.id, f"User: {chat_data.message}\nJarvis: {response}")
    
    return {"response": response}

@app.get("/market/summary")
@limiter.limit("20/minute")
async def market_summary(request: Request, user: models.User = Depends(get_current_user)):
    return finance.get_market_summary()

@app.get("/assistant/notes")
async def get_notes(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    notes = db.query(models.Note).filter(models.Note.user_id == user.id).all()
    # Decrypt notes if they were encrypted
    return notes

# ... other routes follow the same pattern ...
