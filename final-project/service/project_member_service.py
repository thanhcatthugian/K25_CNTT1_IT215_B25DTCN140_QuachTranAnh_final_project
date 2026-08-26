from model.project_member_model import *
from schema.project_member_schema import *
from datetime import datetime
from fastapi import Depends,status,HTTPException
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from utils import *
from sqlalchemy.orm import Session
from model.project_model import *
from model.user_model import *

import logging

logging.basicConfig(
    filename="app.log",
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
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token da het han hoac khong ton tai"
        )

class RoleCheck:
    def __init__(self,role_list:list):
        self.role_list = role_list
    def __call__(self,user_data: dict = Depends(handle_token)):
        if user_data["role"] not in self.role_list:
            logging.warning(f"Nguoi dung co id {user_data["user_id"]} dang truy cap vao chuc nang khong du quyen han")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Khong du quyen han truy cap chuc nang nay"
            )
        return user_data

def add_project_memeber(project_id:int,new_project_member:AddMember,db:Session,user_data:dict = Depends(handle_token)):
    validation = db.query(ProjectMember).filter(ProjectMember.user_id==user_data["user_id"],ProjectMember.project_id==project_id).first()
    if not validation:
        logging.warning(f"Nguoi dung co id{user_data["user_id"]} khong ton tai trong du an")
        return 3
    if validation.role == "owner":
        information = db.query(Project).filter(Project.id==project_id).first()
        if not information:
            logging.warning(f"Khong tim thay project co id{project_id}")
            return None
        is_exist = db.query(User).filter(User.id==new_project_member.user_id).first()
        if not is_exist:
            logging.warning(f"Khong tim thay nguoi dung co id {new_project_member.user_id}")
            return 1
        if is_exist.is_active is False:
            logging.warning(f"User co id {new_project_member.user_id} khong hoat dong")
            return 5
        qualify = db.query(ProjectMember).filter(ProjectMember.user_id==new_project_member.user_id,ProjectMember.project_id==project_id).first()
        if qualify is not None and qualify.is_deleted is True:
            qualify.is_deleted = False
            db.commit()
            logging.info(f"user co id {new_project_member.user_id} da duoc hoi sinh")
            return 6
        if qualify:
            logging.warning(f"user co id {new_project_member.user_id} da ton tai trong project")
            return 2
        if information.is_deleted is True:
            logging.warning(f"Project co id {project_id} da bi xoa")
            return 4
        user_name = db.query(User).filter(User.id==new_project_member.user_id).first()
        totally_new = ProjectMember(
            project_id = project_id,
            user_id = new_project_member.user_id,
            role = "member",
            joined_at = datetime.now(),
            user_name = user_name.full_name,
            is_deleted = False
        )
        db.add(totally_new)
        db.commit()
        db.refresh(totally_new)
        logging.info(f"Them thanh cong thanh vien moi co id {new_project_member.user_id} vao project co id {project_id}")
        return totally_new
    logging.warning(f"Nguoi dung co id {user_data["user_id"]} khong co quyen thuc hien them thanh vien")
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Khong du quyen han truy cap chuc nang nay"
    )

def add_many_member(project_id:int,new_project_member:AddManyMember,db:Session,user_data:dict = Depends(handle_token)):
    fail_append = []
    success_append = []
    validation = db.query(ProjectMember).filter(ProjectMember.user_id==user_data["user_id"],ProjectMember.project_id==project_id).first()
    if not validation:
        return 1
    if validation.role=="owner":
        information = db.query(Project).filter(Project.id==project_id).first()
        if not information:
            return None
        if information.is_deleted is True:
            return 2
        raw_id = new_project_member.model_dump()["user_id"]
        new_members = raw_id.strip().split(",")
        for i in new_members:
            i = int(i)
            is_exist = db.query(User).filter(User.id==i).first()
            if not is_exist:
                fail_append.append(i)
                continue
            if is_exist.is_active is False:
                fail_append.append(i)
                continue
            qualify = db.query(ProjectMember).filter(ProjectMember.user_id==i,ProjectMember.project_id==project_id).first()
            if qualify is not None and qualify.is_deleted is True:
                qualify.is_deleted = False
                success_append.append(i)
            if qualify:
                fail_append.append(i)
                continue
            totally_new = ProjectMember(
            project_id = project_id,
            user_id = i,
            role = "member",
            joined_at = datetime.now(),
            user_name = is_exist.full_name,
            is_deleted = False
                ) 
            success_append.append(i)  
            db.add(totally_new)
            db.commit()
            db.refresh(totally_new)
        return {
            "success_added": success_append,
            "fail_added": fail_append
        }
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail = "Khong du quyen han truy cap chuc nang nay"
    )

    
def show_member_list(project_id:int,db:Session,user_data: dict = Depends(handle_token)):
    validation = db.query(ProjectMember).filter(ProjectMember.user_id==user_data["user_id"],ProjectMember.project_id==project_id).first()
    if not validation:
        logging.warning(f"Nguoi dung co id{user_data["user_id"]} khong ton tai trong du an")
        return 1
    if validation.role == "member" or validation.role == "owner":
        information = db.query(ProjectMember).filter(ProjectMember.project_id==project_id).all()
        if not information:
            logging.warning(f"Khong tim thay project co id{project_id}")
            return None
        logging.info(f"Hien thi danh sach member cua project co id {project_id}")
        return information
    logging.warning(f"Nguoi dung co id {user_data["user_id"]} khong co quyen xem thanh vien")
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Khong du quyen han truy cap"
    )

def soft_delete_member(project_id:int,user_id:int,db:Session,user_data:dict = Depends(handle_token)):
    validation = db.query(ProjectMember).filter(ProjectMember.project_id==project_id,ProjectMember.user_id==user_data["user_id"]).first()
    if not validation:
        logging.warning(f"Nguoi dung co id{user_data["user_id"]} khong ton tai trong du an")
        return 1
    if validation.role == "owner":
        information = db.query(ProjectMember).filter(ProjectMember.project_id==project_id,ProjectMember.user_id==user_id).first()
        if not information:
            logging.warning(f"Khong tim thay project co id{project_id}")
            return None
        if information.is_deleted is True:
            logging.warning(f"thanh vien co id {user_id} da bi xoa tu truoc")
            return 2
        information.is_deleted = True
        db.commit()
        db.refresh(information) 
        logging.info(f"Thanh vien co id {user_id} da bi xoa khoi project co id {project_id}")
        return information
    logging.warning(f"Nguoi dung co id {user_data["user_id"]} khong co quyen xoa thanh vien")
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Khong du quyen truy cap chuc nang nay"
    )