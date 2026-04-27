# handels pswd hashing and JWT management 

from datetime import datetime , timedelta , timezone 
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#psswd setup

def get_password_hash(password : str) -> str:
  return pwd_context.hash(password)

def verify_password(plain_password: str , hashed_password: str) -> bool:
  return pwd_context.verify(plain_password, hashed_password)

#setup jwt

def create_access_token(data: dict):

  to_encode = data.copy()

  expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
  to_encode.update({"exp": expire})

  return jwt.encode(to_encode, settings.JWT_SECRET , algorithm=settings.ALGORITHM)

#setup jwt decode 
def decode_access_token(token:str):
  try: 
    payload = jwt.decode(token , settings.JWT_SECRET , algorithms=[settings.ALGORITHM])
    return payload if payload.get("sub") else None
  except JWTError:
    return None
