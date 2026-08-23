from schema.comment_schema import *
from model.comment_model import *
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from fastapi import Depends,HTTPException,status
from utils import *
from sqlalchemy.orm import Session
from model.task_model import *
from model.project_model import *
from model.project_member_model import *

import logging

logging.basicConfig(
    filename="task.log",
    level=logging.INFO,
    format= "%(asctime)s + %(levelname)s + %(message)s",
    encoding="utf-8"
)


SECURITY_KEY = HTTPBearer()

def handle_token(cre:HTTPAuthorizationCredentials = Depends(SECURITY_KEY)):
    token = cre.credentials
    try:
        information = read_access_token(token)
        return information
    except jwt.ExpiredSignatureError or jwt.InvalidTokenError:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail= "Token da het han / khong ton tai"
        )

class RoleCheck:
    def __init__(self,role_list:list):
        self.role_list = role_list
    def __call__(self, user_data: dict = Depends(handle_token)):
        if user_data["role"] not in self.role_list:
            logging.warning(f"Nguoi dung co id {user_data["user_id"]} dang truy cap vao chuc nang khong du quyen han")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Khong du quyen han truy cap chuc nang nay"
            )
        return user_data

def add_comment(task_id: int,new_comment:CreateComment,db:Session,user_data:dict = Depends(handle_token)):
    is_exist = db.query(Task).filter(Task.id==task_id).first()
    if not is_exist:
        logging.warning(f"Khong tim thay task co id {task_id}")
        return 5
    if is_exist.is_deleted is True:
        logging.warning(f"Task co id {task_id} da bi xoa")
        return 1
    validation = db.query(Project).filter(Project.id==is_exist.project_id).first()
    if validation.is_deleted is True:
        logging.warning(f"Project co id {is_exist.project_id} da bi xoa")
        return 2
    qualify = db.query(ProjectMember).filter(ProjectMember.project_id==validation.id,ProjectMember.user_id==user_data["user_id"]).first()
    if not qualify:
        logging.warning(f"Nguoi dung co id {user_data["user_id"]} khong co trong project")
        return 4
    if qualify.is_deleted is True:
        logging.warning(f"Nguoi dung co id {user_data["user_id"]} khong con trong du an")
        return 3
    if qualify.role == "member" or qualify.role == "owner":
        totally_new = Comment(
            comment_text = new_comment.comment_text,
            task_id = task_id
        )
        db.add(totally_new)
        db.commit()
        db.refresh(totally_new)
        logging.info(f"Da them thanh cong comment co id {totally_new.id}")
        return totally_new
    logging.warning(f"Nguoi dung co id {user_data["user_id"]} khong co quyen thuc hien them comment")
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail = "Khong du quyen truy cap chuc nang nay"
    )

