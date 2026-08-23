from .auth_service import *
from schema.user_schema import *
from model.user_model import *
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from fastapi import Depends,HTTPException,status
from sqlalchemy import or_


import logging

logging.basicConfig(
    filename="user.log",
    level=logging.INFO,
    format= "%(asctime)s + %(levelname)s + %(message)s",
    encoding="utf-8"
)

SECURITY_KEY = HTTPBearer()

def handle_token(cre:HTTPAuthorizationCredentials = Depends(SECURITY_KEY)):
    token = cre.credentials
    try:
        information = read_access_token(token)
        logging.info(f"Lay thanh cong thong tin nguoi dung co id: {information["user_id"]}")
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

def show_through_id(keyword:str,status_keyword:str,db:Session):
    data = []
    if keyword is None and status_keyword is None:
      information = db.query(User).all()
    if keyword is not None:
        keyword = keyword.lower()
    if status_keyword is not None:
        status_keyword==status_keyword.lower()
    if status_keyword is not None and keyword is None:
        if status_keyword in ["true","1"]:
            information = db.query(User).filter(User.is_active==True).all()
        elif status_keyword in ["false","0"]:
            information = db.query(User).filter(User.is_active == False).all()
    elif keyword is not None and status_keyword is None:
        information = db.query(User).filter( or_ (User.full_name.ilike(f"%{keyword}%"),User.email.ilike(f"%{keyword}%"))).all()
    else:
        if status_keyword in ["true","1"]:
            information = db.query(User).filter(or_ (User.full_name.ilike(f"%{keyword}%"),User.email.ilike(f"%{keyword}%")), User.is_active == True).all()
        elif status_keyword in ["false","0"]:
            information = db.query(User).filter(or_ (User.full_name.ilike(f"%{keyword}%"),User.email.ilike(f"%{keyword}%")), User.is_active == False).all()
    if not information:
        logging.warning(f"Khong tim thay thong tin cua user co thong tin tim kiem keyword: {keyword}, status_keyword: {status_keyword}")
        return None
    for i in information:
        data.append({
            "role": i.role,
            "full_name": i.full_name,
            "email": i.email,
            "is_active": i.is_active
        })
    logging.info(f"lay thanh cong thong tin cua user co thong tin tim kiem keyword:{keyword}, status_keyword: {status_keyword}")
    return data

    