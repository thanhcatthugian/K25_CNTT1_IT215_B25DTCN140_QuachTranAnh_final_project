from schema.task_schema import *
from model.task_model import *
from fastapi import Depends,HTTPException,status,File,UploadFile
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from utils import *
from sqlalchemy.orm import Session
from datetime import datetime
from model.project_member_model import *
import os,uuid,shutil
SECURITY_KEY = HTTPBearer()

def handle_token(cre:HTTPAuthorizationCredentials = Depends(SECURITY_KEY)):
    token = cre.credentials
    try:
        information = read_access_token(token)
        return information
    except jwt.ExpiredSignatureError or jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token da het han / khong ton tai"
        )


class RoleCheck:
    def __init__(self,role_list:list):
        self.role_list = role_list
    def __call__(self, user_data:dict = Depends(handle_token)):
        if user_data["role"] not in self.role_list:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Khong co quyen truy cap chuc nang nay"
            )
        return user_data
    

def add_task(project_id:int,new_task:CreateTask,db:Session,user_data:dict = Depends(handle_token)):
    information = db.query(ProjectMember).filter(ProjectMember.project_id==project_id).first()
    if not information:
        return None
    validation = db.query(ProjectMember).filter(ProjectMember.user_id==user_data["user_id"],ProjectMember.project_id==project_id).first()
    if not validation:
        return None
    if validation.role=="member":
        totally_new = Task(
            title = new_task.title,
            description = new_task.description,
            status = new_task.status,
            priority = new_task.priority,
            created_at = datetime.now(),
            due_date = None,
            project_id = project_id,
            assignee_id = new_task.assignee_id
        )
        db.add(totally_new)
        db.commit()
        db.refresh(totally_new)
        return totally_new
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Khong du quyen truy cap"
    )

def show_tasks(project_id:int,db:Session,user_data:dict = Depends(handle_token)):
    validation = db.query(ProjectMember).filter(ProjectMember.user_id==user_data["user_id"],ProjectMember.project_id==project_id).first()
    if not validation:
        return None
    if validation.role=="member":
        information = db.query(Task).filter(Task.project_id==project_id).all()
        if not information:
            return None
        return information
    raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Khong du quyen truy cap"
        )

def show_through_id(task_id:int,db:Session,user_data:dict = Depends(handle_token)):
    validation = db.query(ProjectMember).filter(ProjectMember.user_id==user_data["user_id"]).first()
    if not validation:
        return None
    if validation == "member":
        information = db.query(Task).filter(Task.id==task_id).first()
        if not information:
            return None
        return information
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Khong du quyen truy cap"
    )

def update_task_information(task_id:int,db:Session,new_task:CreateTask,user_data:dict = Depends(handle_token)):
    validation = db.query(ProjectMember).filter(ProjectMember.user_id==user_data["user_id"]).first()
    if not validation:
        return None
    if validation.role=="member" or validation.role=="owner":
        information = db.query(Task).filter(Task.id==task_id).first()
        if not information:
            return None
        data = new_task.model_dump(exclude_unset=True)
        if "due_date" in data:
            try:
                data["due_date"] = datetime.fromisoformat(data["due_date"])
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail = "Can truyen dung dinh dang YYYY-MM-DD / YYYY-MM-DDTHH:MM:SS"
                )
        for key,value in data.items():
            setattr(information,key,value)
        db.commit()
        db.refresh(information)
        return information
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Khong du quyen truy cap"
    )

def remove_task_information(task_id:int,db:Session,user_data:dict = Depends(handle_token)):
    validation = db.query(ProjectMember).filter(ProjectMember.user_id==user_data["user_id"]).first()
    if not validation:
        return None
    if validation.role=="member" or validation.role=="owner":
        information = db.query(Task).filter(Task.id==task_id).first()
        if not information:
            return None
        db.delete(information)
        db.commit()
        return information
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Khong du quyen truy cap"
    )

file_types = ["jpg","png","pdf","docx"]

DIR_UPLOAD_FILE = "upload/files"
os.makedirs(DIR_UPLOAD_FILE,exist_ok=True)
def handle_upload_file(file:UploadFile = File(...)):
    type_file = file.filename.split(".")[-1]
    if type_file not in file_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dinh dang file can la jpg,png,pdf hoac docx"
        )
    new_file_name = f"{uuid.uuid4().hex}.{type_file}"
    url_image_create = os.path.join(DIR_UPLOAD_FILE,new_file_name)

    with open(url_image_create,"wb") as buffer:
        shutil.copyfileobj(file.file,buffer)
    return file.filename

def upload_file(task_id:int ,db:Session = Depends,file:UploadFile = File(...),user_data:dict = Depends(handle_token)):
    validation = db.query(ProjectMember).filter(ProjectMember.user_id==user_data["user_id"]).first()
    if not validation:
        return None
    if validation.role=="member":
        information = db.query(Task).filter(Task.id==task_id).first()
        if not information:
            return None
        information.attach_file = handle_upload_file(file)
        db.commit()
        db.refresh(information)
        return information
    raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Khong du quyen truy cap"
        )

def add_commet(task_id:int,db:Session,user_data:dict = Depends(handle_token)):
    validation = db.query(ProjectMember).filter(ProjectMember.user_id==user_data["user_id"],Task.project_id==ProjectMember.project_id).first()
    