from schema.project_schema import *
from model.project_model import *
from sqlalchemy.orm import Session
from utils import *
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from fastapi import Depends,HTTPException,status,Request
from datetime import datetime
from sqlalchemy.orm import joinedload
from database import *
from model.project_member_model import *
from model.user_model import *
import logging

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format= "%(asctime)s + %(levelname)s + %(message)s",
    encoding="utf-8"
)


SECURITY_KEY  =HTTPBearer()

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
    def __call__(self, user_data: dict = Depends(handle_token)):
        if user_data["role"] not in self.role_list:
            logging.warning(f"Nguoi dung co id {user_data["user_id"]} dang truy cap vao chuc nang khong du quyen han")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Khong du quyen han truy cap"
            )
        return user_data


def add_project(new_project:CreateProject,db:Session,user_data:dict = Depends(handle_token)):
    totally_new = Project(
        name = new_project.name,
        description = new_project.description,
        owner_id = user_data["user_id"],
        created_at = datetime.now(),
        is_deleted = False
    )
    db.add(totally_new)
    db.commit()
    logging.info(f"da tao thanh cong mot project moi co id {totally_new.id}")
    new_mem_name = db.query(User).filter(User.id==user_data["user_id"]).first()
    totally_new_mem = ProjectMember(
        project_id = totally_new.id,
        user_id = user_data["user_id"],
        role = "owner",
        joined_at = datetime.now(),
        user_name = new_mem_name.full_name,
        is_deleted = False
    )
    db.add(totally_new_mem)
    db.commit()
    db.refresh(totally_new)
    logging.info(f"Da them thanh cong mot member cho project voi quyen han {totally_new_mem.role}")
    return totally_new

def show_own_project(db:Session,keyword:str,user_data:dict = Depends(handle_token)):
    if keyword is None:
        information = db.query(ProjectMember).filter(ProjectMember.user_id==user_data["user_id"]).all()
    elif keyword is not None:
        keyword = keyword.lower()
        information = db.query(Project).filter(Project.name.ilike(f"%{keyword}%")).all()
    if not information:
        logging.warning("Khong tim thay thong tin project tuong ung")
        return None
    logging.info(f"Tim thay thong tin project voi keyword {keyword}")
    return information

def show_through_id(project_id:int,db:Session,user_data:dict = Depends(handle_token)):
    validation = db.query(ProjectMember).filter(ProjectMember.user_id==user_data["user_id"],ProjectMember.project_id==project_id).first()
    if not validation:
        logging.warning(f"Nguoi dung khong ton tai trong du an co id {project_id}")
        return 1
    if validation.role == "member" or validation.role == "owner":
        information = db.query(Project).filter(Project.id==project_id).first()
        if not information:
            logging.warning(f"Khong tim thay du an co id {project_id}")
            return None
        logging.info(f"Lay thanh cong thong tin du an co id {project_id}")
        return information
    logging.warning(f"Nguoi dung co id {user_data["user_id"]} dang truy cap vao chuc nang khong du quyen han")
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Khong du quyen han truy cap chuc nang nay"
    )

def update_information(project_id:int,new_project:CreateProject,db:Session,user_data: dict = Depends(handle_token)):
    validation = db.query(ProjectMember).filter(ProjectMember.user_id==user_data["user_id"],ProjectMember.project_id==project_id).first()
    if not validation:
        logging.warning(f"Nguoi dung co id {user_data["user_id"]} khong ton tai trong du an")
        return 1
    if validation.role == "owner":
        information = db.query(Project).filter(Project.id==project_id).first()
        if not information:
            logging.warning(f"Khong tim thay du an co id{project_id}")
            return None
        if information.is_deleted is True:
            logging.warning(f"Du an co id {project_id} da bi xoa")
            return 2
        update_data = new_project.model_dump(exclude_unset=True)
        for key,value in update_data.items():
            setattr(information,key,value)
        db.commit()
        db.refresh(information)
        logging.info(f"Da cap nhat thanh cong thong tin cho project co id{project_id}")
        return information
    logging.warning(f"Nguoi dung co id {user_data["user_id"]} khong co du quyen han cap nhat du an")
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Khong du quyen han truy cap chuc nang nay"
    )

def soft_delete_project(project_id:int,db:Session,user_data:dict = Depends(handle_token)):
    validation = db.query(ProjectMember).filter(ProjectMember.user_id==user_data["user_id"],ProjectMember.project_id==project_id).first()
    if not validation:
        logging.warning(f"Nguoi dung co id {user_data["user_id"]} khong ton tai trong du an")
        return 1
    if validation.role == "owner":
        information = db.query(Project).filter(Project.id==project_id).first()
        if not information:
            logging.warning(f"Khong tim thay thong tin project co id{project_id}")
            return None
        if information.is_deleted is True:
            logging.warning(f"Du an co id {project_id} da bi xoa")
            return 2
        linking_information = db.query(ProjectMember).filter(ProjectMember.project_id==project_id).all()
        information.is_deleted = True
        for i in linking_information:
            i.is_deleted = True
        db.commit()
        db.refresh(information)
        logging.info(f"Da xoa thanh cong project co id {project_id}")
        return information
    logging.warning(f"Nguoi dung co id {user_data["user_id"]} khong co quyen han truy cap chuc nang xoa project")
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail = "Khong du quyen truy cap chuc nang nay"
    )
