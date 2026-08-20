from model.project_member_model import *
from schema.project_member_schema import *
from datetime import datetime
from fastapi import Depends,status,HTTPException
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from utils import *
from sqlalchemy.orm import Session
from model.project_model import *
from model.user_model import *
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
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Khong du quyen han truy cap chuc nang nay"
            )
        return user_data

def add_project_memeber(project_id:int,new_project_member:AddMember,db:Session,user_data:dict = Depends(handle_token)):
    validation = db.query(ProjectMember).filter(ProjectMember.user_id==user_data["user_id"],ProjectMember.project_id==project_id).first()
    is_owner = False
    if validation and validation.role=="owner":
        is_owner = True
    is_admin = user_data["role"]=="admin"
    
    if is_admin or is_owner:
        information = db.query(Project).filter(Project.id==project_id).first()
        if not information:
            return None
        is_exist = db.query(User).filter(User.id==new_project_member.user_id).first()
        if not is_exist:
            return 1
        totally_new = ProjectMember(
            project_id = project_id,
            user_id = new_project_member.user_id,
            role = new_project_member.role,
            joined_at = datetime.now()
        )
        db.add(totally_new)
        db.commit()
        db.refresh(totally_new)
        return totally_new
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Khong du quyen han truy cap chuc nang nay"
    )
    
def show_member_list(project_id:int,db:Session,user_data: dict = Depends(handle_token)):
    validation = db.query(ProjectMember).filter(ProjectMember.user_id==user_data["user_id"]).first()
    if not validation:
        return None
    if validation.role == "member":
        information = db.query(ProjectMember).filter(ProjectMember.project_id==project_id).all()
        if not information:
            return None
        return information
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Khong du quyen han truy cap"
    )

def remove_information(project_id:int,user_id:int,db:Session,user_data:dict = Depends(handle_token)):
    validation = db.query(ProjectMember).filter(ProjectMember.user_id==user_data["user_id"]).first()
    if not validation:
        return None
    if validation.role=="owner":
        information = db.query(ProjectMember).filter(ProjectMember.project_id==project_id,ProjectMember.user_id==user_id).first()
        if not information:
            return None
        db.delete(information)
        db.commit()
        return information
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Khong du quyen han truy cap chuc nang nay"
    )

