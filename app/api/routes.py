from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status, APIRouter, UploadFile, File, Form, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
from .utility import auth, rag, user
from app.models import schemas
from app.core import database
from sqlalchemy.orm import Session
from pathlib import Path
from fastapi.responses import JSONResponse
import os
import shutil
import tempfile
from dotenv import load_dotenv
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from app.models import users 
from app.core.security import hash_password  
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

router = APIRouter()
app = FastAPI()
limiter = Limiter(key_func=get_remote_address)
get_db = database.get_db

@app.exception_handler(RateLimitExceeded)
async def ratelimit(request, exc):
    return {"error": "Rate limit exceeded, try again later"}

@router.post("/login_token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
) -> schemas.Token:
    user_obj = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username and password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user_obj.username},
        expires_delta=access_token_expires
    )
    return schemas.Token(access_token=access_token, token_type="bearer")

@router.get("/users/me", response_model=schemas.UserResponse)
@limiter.limit("10/minute")
async def read_users_me(
    request: Request,
    current_user: Annotated[schemas.User, Depends(auth.get_current_active_user)],
    db: Session = Depends(get_db)
):
    logger.info(f"Received request to /users/me from {request.client.host}")
    logger.info(f"Current user: {current_user.username}")
    return current_user

@router.post("/user_create", response_model=schemas.UserResponse)
async def create_user(user: schemas.User, db: Session = Depends(get_db)):
    # Check for existing user
    if db.query(users.User).filter(users.User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    if db.query(users.User).filter(users.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = users.User(
        username=user.username,
        email=user.email,
        password=hash_password(user.password), 
        base_role=user.base_role,
        auth_role="user",  
        is_deleted=False   
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return schemas.UserResponse.from_orm(db_user)

@router.post("/user/logout")
async def logout():
    return {"message": "Logged out"}

@router.put("/update_user/{id}", response_model=schemas.User)
async def update_user(
    id: int,
    user: schemas.User,
    current_user: Annotated[schemas.User, Depends(auth.get_current_active_user)],
    db: Session = Depends(get_db)
):
    # Fetch the existing user
    db_user = db.query(users.User).filter(users.User.id == id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check authorization 
    if db_user.username != current_user.username and current_user.auth_role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update this user")
    
    db_user.username = user.username
    db_user.email = user.email
    db_user.base_role = user.base_role
    if user.password:  
        db_user.password = hash_password(user.password)
    
    db.commit()
    db.refresh(db_user)
    return schemas.User.from_orm(db_user)

@router.delete("/delete/user/{id}")
async def delete_user(
    id: int,
    current_user: Annotated[schemas.User, Depends(auth.get_current_active_user)],
    db: Session = Depends(get_db)
):
    return user.del_user(id, db)

@router.post("/upload/")
@limiter.limit("3/minute")
async def upload_file(
    request: Request,
    current_user: Annotated[schemas.User, Depends(auth.get_current_active_user)],
    file: UploadFile = File(...),
    question: str = Form(...)
):
    try:
        current_user_role = current_user.base_role
        file_extension = Path(file.filename).suffix

        # Temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
        
        # Call RAG pipeline for processing
        try:
            transcription = rag.rag_response(temp_file_path, question, file_extension, current_user_role)
        
        finally:
            os.remove(temp_file_path)

        return JSONResponse(content={"generated_answer": transcription})

    except Exception as e:
        return JSONResponse(content={"detail": str(e)}, status_code=400)