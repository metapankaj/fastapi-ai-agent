from pydantic import BaseModel,EmailStr,Field,field_validator
from enum import Enum
import re 



class BaseRole(str,Enum):
    lawyer = "lawyer"
    student = "student"
    enterprise = "enterprise"
    banker = "banker"


class AuthRole(str,Enum):
    user:str
    admin:str



class User(BaseModel):
    """Schema for creating a new user."""
    
    username: str = Field(...,min_length=5,max_length= 50)
    email: EmailStr = Field(...,max_length=50)
    password: str = Field(...,min_length=10,max_length=60)
    base_role: str = Field(...)
    
    #for password complexiety
    @field_validator('password')
    def validate_password(cls,value):
        if not isinstance(value,str):
            raise ValueError('password must be a string')
        
        #regex
        pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[^A-Za-z0-9]).{10,60}$"
        
        if not re.match(pattern, value):
            raise ValueError(
                """Password must contain at least one uppercase letter,
                  one lowercase letter, one number, and one special character,
                  and be min 10 characters"""
            )
        return value
    
    
    class Config():
        from_attributes = True
    
    
class UserInDB(User):
    """Schema for user data as stored in the database."""
    
    id:int
    username:str 
    password:str
    

class UserResponse(BaseModel):
    """ Schema for returning user data. """
    username: str 
    email:EmailStr
    base_role:str
    
    class Config():
        from_attributes = True

class Login(BaseModel):
    """Schema for user login credentials."""
    
    username: str = Field(...,min_length=5)
    password:str = Field(...,min_length=10)
    

    
    

class Token(BaseModel):
    """Schema for JWT token response."""
    access_token:str
    token_type:str = "bearer"
    
class TokenPayload(BaseModel):
    """Schema for JWT token payload."""
    
    username:str | None = None
    role: BaseRole | None = None
    

