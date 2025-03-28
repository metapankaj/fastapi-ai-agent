from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#hashing plain password
def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)

#verifying plain password with hashed password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except ValueError:
        return False