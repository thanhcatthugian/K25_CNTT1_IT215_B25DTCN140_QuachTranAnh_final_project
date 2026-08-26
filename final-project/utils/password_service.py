import bcrypt 
import jwt
from datetime import datetime,timezone,timedelta
from setting import settings

SECRET_KEY = settings.secret_key

def ground_password (raw_password:str)->str:
    byte_transfer = raw_password.encode("utf-8")
    verified_password = bcrypt.hashpw(byte_transfer,salt=bcrypt.gensalt())
    return verified_password.decode()

def check_password(given_password:str,data_password:str)->bool:
    return bcrypt.checkpw(given_password.encode("utf-8"),data_password.encode("utf-8"))

def create_access_token(payload:dict)->str:
    time_now = datetime.now(timezone.utc)
    payload.update({
        "iat": time_now,
        "exp": time_now+timedelta(minutes=settings.expired_time)
    })
    return jwt.encode(payload=payload,key=SECRET_KEY,algorithm="HS256")

def read_access_token(token:str)->dict:
    return jwt.decode(token,key=SECRET_KEY,algorithms=["HS256"])