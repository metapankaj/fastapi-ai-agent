from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    database_url: str 
    secret_key: str 
    algorithm: str 
    access_token_expire_minutes: int
    session_cookie_name:str

SETTINGS = Settings()
