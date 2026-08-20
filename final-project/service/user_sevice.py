from .auth_service import *
from schema.user_schema import UserResponse
from model.user_model import *
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from fastapi import Depends,HTTPException,status
from sqlalchemy import or_

SECURITY_KEY = HTTPBearer()

def handle_token(cre:HTTPAuthorizationCredentials = Depends(SECURITY_KEY)):
    token = cre.credentials
    try:
        information = read_access_token(token)
        return {
            "role": information["role"],
            "email": information["sub"],
            "fullname" :information["full_name"],
            "is_active": information["is_active"]
        }
    except jwt.ExpiredSignatureError or jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token da het han hoac khong ton tai"
        )


class RoleCheck:
    def __init__(self,role_list:list):
        self.role_list = role_list
    def __call__(self, user_data: dict = Depends(handle_token)):
        role_name = user_data["role"]
        if role_name not in self.role_list:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Khong du quyen truy cap chuc nang nay"
            )
        return user_data

def show_through_id(keyword:str,db:Session):
    if keyword is None:
        return db.query(User).all()
    keyword = keyword.lower()
    if keyword in ["true","1"]:
        information = db.query(User).filter(User.is_active == True).all()
    elif keyword in ["false","0"]:
        information = db.query(User).filter(User.is_active == False).all()
    else:
        information = db.query(User).filter( or_ (User.full_name.ilike(f"%{keyword}%"),User.email.ilike(f"%{keyword}%"))).all()
    if not information:
        return None
    return information

    