from sqlalchemy import Column,Boolean, Integer, String,Enum
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True,nullable= False)
    email = Column(String, unique=True, index=True,nullable=False)
    password = Column(String,nullable=False)
    base_role = Column(Enum("lawyer","student","banker","enterprise",name = "base_role"),nullable=False)
    auth_role = Column(Enum("user","admin",name="auth_role"),default="user",nullable=False)
    is_deleted = Column(Boolean, default=False, index=True)
    
