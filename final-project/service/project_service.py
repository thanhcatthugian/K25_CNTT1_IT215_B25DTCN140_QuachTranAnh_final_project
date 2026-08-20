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
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Khong du quyen han truy cap"
            )
        return user_data


def add_project(new_project:CreateProject,db:Session,user_data:dict = Depends(handle_token)):
    totally_new = Project(
        name = new_project.name,
        description = new_project.description,
        owner_id = new_project.owner_id,
        created_at = datetime.now()
    )
    totally_new_mem = ProjectMember(
            project_id = totally_new.id,
            user_id = user_data["user_id"],
            role = "owner",
            joined_at = datetime.now()
        )
    db.add(totally_new_mem)
    db.commit()
    db.refresh(totally_new_mem)
    db.add(totally_new)
    db.commit()
    db.refresh(totally_new)
    return totally_new

def show_own_project(db:Session,keyword:str,user_data:dict = Depends(handle_token)):
    keyword = keyword.lower()
    if keyword is None:
        information = db.query(Project).filter(Project.owner_id==user_data["user_id"]).all()
    information = db.query(Project).filter(Project.name.ilike(f"%{keyword}%")).all()
    if not information:
        return None
    return information

def show_through_id(project_id:int,db:Session,user_data:dict = Depends(handle_token)):
    validation = db.query(ProjectMember).filter(ProjectMember.user_id==user_data["user_id"],ProjectMember.project_id==project_id).first()
    if not validation:
        return None
    if validation.role == "member":
        information = db.query(Project).filter(Project.id==project_id).first()
        if not information:
            return None
        return information
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Khong du quyen han truy cap chuc nang nay"
    )

def update_information(project_id:int,new_project:CreateProject,db:Session,user_data: dict = Depends(handle_token)):
    validation = db.query(ProjectMember).filter(ProjectMember.user_id==user_data["user_id"],ProjectMember.project_id==project_id).first()
    if not validation:
        return None
    if validation.role == "owner":
        information = db.query(Project).filter(Project.id==project_id).first()
        if not information:
            return None
        update_data = new_project.model_dump(exclude_unset=True)
        for key,value in update_data.items():
            setattr(information,key,value)
        db.commit()
        db.refresh(information)
        return information
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Khong du quyen han truy cap chuc nang nay"
    )

def remove_information(project_id:int,db:Session,user_data:dict = Depends(handle_token)):
    validation = db.query(ProjectMember).filter(ProjectMember.user_id==user_data["user_id"],ProjectMember.project_id==project_id).first()
    if not validation:
        return None
    if validation.role=="owner":
        information = db.query(Project).filter(Project.id==project_id).first()
        if not information:
            return None
        db.query(ProjectMember).filter(ProjectMember.project_id==project_id).delete()
        db.delete(information)
        db.commit()
        return information
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Khong du quyen han truy cap chuc nang nay"
    )
