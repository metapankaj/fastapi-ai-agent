from typing import Annotated
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.models import users  
from app.core import database  
from app.core.security import verify_password
from app.models import schemas 
from app.core.config import SETTINGS
from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use OAuth2PasswordBearer to extract the token from the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login_token")

get_db = database.get_db

def get_user(db: Session, username: str):
    user = db.query(users.User).filter(users.User.username == username).first()
    return user

def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user or not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a new JWT token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=SETTINGS.access_token_expire_minutes))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SETTINGS.secret_key, algorithm=SETTINGS.algorithm)
    logger.debug(f"Created token with payload: {to_encode}")
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SETTINGS.secret_key, algorithms=[SETTINGS.algorithm])
        username: str = payload.get("sub")
        if username is None:
            logger.error("No 'sub' claim in token")
            raise credentials_exception
        token_data = schemas.TokenPayload(username=username)
    except InvalidTokenError as e:
        logger.error(f"Token validation failed: {str(e)}")
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        logger.error(f"User not found: {token_data.username}")
        raise credentials_exception
    return schemas.User.from_orm(user)

async def get_current_active_user(
    current_user: Annotated[schemas.User, Depends(get_current_user)],
):
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")
    return current_user