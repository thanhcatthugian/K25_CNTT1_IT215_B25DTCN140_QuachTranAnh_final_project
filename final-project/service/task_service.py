from schema.task_schema import *
from model.task_model import *
from fastapi import Depends,HTTPException,status,File,UploadFile
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from utils import *
from sqlalchemy.orm import Session
from datetime import datetime
from model.project_member_model import *
import os,uuid,shutil
from sqlalchemy import or_
from model.project_model import *

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
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token da het han / khong ton tai"
        )


class RoleCheck:
    def __init__(self,role_list:list):
        self.role_list = role_list
    def __call__(self, user_data:dict = Depends(handle_token)):
        if user_data["role"] not in self.role_list:
            logging.warning(f"Nguoi dung co id {user_data["user_id"]} dang truy cap vao chuc nang khong du quyen han")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Khong co quyen truy cap chuc nang nay"
            )
        return user_data
    

def add_task(project_id:int,new_task:CreateTask,db:Session,user_data:dict = Depends(handle_token)):
    information = db.query(Project).filter(Project.id==project_id).first()
    if not information:
        logging.warning(f"Khong tim thay project co id {project_id}")
        return None
    if information.is_deleted is True:
        logging.warning(f"Project co id {project_id} da bi xoa")
        return 1
    validation = db.query(ProjectMember).filter(ProjectMember.user_id==user_data["user_id"],ProjectMember.project_id==project_id).first()
    if not validation:
        logging.warning(f"Nguoi dung co id {user_data["user_id"]} khong co trong project")
        return 2
    if validation.role=="member" or validation.role == "owner":
        totally_new = Task(
            title = new_task.title,
            description = new_task.description,
            status = new_task.status,
            priority = new_task.priority,
            created_at = datetime.now(),
            due_date = None,
            project_id = project_id,
            assignee_id = None,
            is_deleted = False  
        )
        db.add(totally_new)
        db.commit()
        db.refresh(totally_new)
        logging.info(f"Them thanh cong mot task moi co id {totally_new.id}")
        return totally_new
    logging.warning(f"Nguoi dung co id {user_data["user_id"]} khong co quyen thuc hien them task")
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Khong du quyen truy cap"
    )

def show_tasks(project_id:int,db:Session,user_data:dict = Depends(handle_token)):
    validation = db.query(ProjectMember).filter(ProjectMember.user_id==user_data["user_id"],ProjectMember.project_id==project_id).first()
    if not validation:
        logging.warning(f"Nguoi dung co id {user_data["user_id"]} khong co trong project")
        return 1
    qualify = db.query(Project).filter(Project.id==project_id).first()
    if qualify.is_deleted is True:
        logging.warning(f"Project co id {project_id} da bi xoa")
        return 2
    if validation.role=="member" or validation.role == "owner":
        information = db.query(Task).filter(Task.project_id==project_id).all()
        if not information:
            logging.warning(f"Khong tim thay task cua project co id {project_id}")
            return None
        logging.info("Hien thi toan bo task")
        return information
    logging.warning(f"Nguoi dung co id {user_data["user_id"]} khong co quyen thuc hien hien thi task")
    raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Khong du quyen truy cap"
        )

def show_through_id(task_id:int,db:Session,user_data:dict = Depends(handle_token)):
    validation = db.query(ProjectMember).filter(ProjectMember.user_id==user_data["user_id"]).first()
    if not validation:
        return None
    if validation.role == "member" or validation.role == "owner":
        information = db.query(Task).filter(Task.id==task_id).first()
        in_project = db.query(ProjectMember).filter(ProjectMember.user_id==user_data["user_id"],ProjectMember.project_id==information.project_id).all()
        if not in_project:
            logging.warning(f"Nguoi dung co id {user_data["user_id"]} khong co trong project")
            return 2
        if not information:
            logging.warning(f"Khong tim thay task co id {task_id}")
            return None
        logging.info(f"Hien thi task co id {task_id}")
        return information
    logging.warning(f"Nguoi dung co id {user_data["user_id"]} khong co quyen thuc hien hien thi task")
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Khong du quyen truy cap"
    )

def update_task_information(task_id:int,db:Session,new_task:UpdateTask,user_data:dict = Depends(handle_token)):
    validation = db.query(ProjectMember).filter(ProjectMember.user_id==user_data["user_id"]).first()
    if not validation:
        return None
    if  validation.role=="owner" or validation.role == "member":
        information = db.query(Task).filter(Task.id==task_id).first()
        if not information:
            logging.warning(f"Khong tim thay task co id {task_id}")
            return None
        in_project = db.query(ProjectMember).filter(ProjectMember.user_id==user_data["user_id"],ProjectMember.project_id==information.project_id).all()
        if not in_project:
            logging.warning(f"Nguoi dung co id {user_data["user_id"]} khong co trong project")
            return 2
        data = new_task.model_dump(exclude_unset=True)
        if "due_date" in data:
            try:
                data["due_date"] = datetime.fromisoformat(data["due_date"])
            except ValueError:
                logging.warning("Dinh dang cua ngay thang dang bi nhap sai")
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail = "Can truyen dung dinh dang YYYY-MM-DD / YYYY-MM-DDTHH:MM:SS"
                )
        qualify = db.query(ProjectMember).filter(ProjectMember.user_id==user_data["user_id"],ProjectMember.user_id==new_task.assignee_id).first()
        if not qualify:
            logging.warning(f"Nguoi dung co id {new_task.assignee_id} khong thuoc du an")
            return 1
        if information.is_deleted is True:
            logging.warning(f"Task co id {task_id} da bi xoa")
            return 3
        for key,value in data.items():
            setattr(information,key,value)
        db.commit()
        db.refresh(information)
        logging.info(f"da cap nhat thanh cong thong tin cho task co id {task_id}")
        return information
    logging.warning(f"Nguoi dung co id {user_data["user_id"]} khong co quyen thuc hien cap nhat task")
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Khong du quyen truy cap"
    )

def soft_delete_task(task_id:int,db:Session,user_data:dict = Depends(handle_token)):
    information = db.query(Task).filter(Task.id==task_id).first()
    validation = db.query(ProjectMember).filter(ProjectMember.user_id==user_data["user_id"],ProjectMember.project_id==information.project_id).first()
    if not validation:
        logging.warning(f"Nguoi dung co id {user_data["user_id"]} khong co trong project")
        return 1
    if information.is_deleted is True:
        logging.warning(f"Task co id {task_id} da bi xoa")
        return 2
    if validation.role == "owner":
        if not information :
            logging.warning(f"Khong tim thay task co id {task_id}")
            return None
        information.is_deleted = True
        db.commit()
        db.refresh(information)
        logging.info(f"Xoa thanh cong task co id {task_id}")
        return information
    logging.warning(f"Nguoi dung co id {user_data["user_id"]} khong co quyen thuc hien xoa task")
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail = "Khong du quyen truy cap chuc nang nay"
    )
        



def find_task_by_keyword(project_id:int,keyword:str,db:Session,user_data:dict = Depends(handle_token)):
    validation = db.query(ProjectMember).filter(ProjectMember.user_id==user_data["user_id"],ProjectMember.project_id==project_id).first()
    if not validation:
        logging.warning(f"Nguoi dung co id {user_data["user_id"]} khong co trong project")
        return 1
    if validation.role == "member" or validation == "owner":
        verify = db.query(Project).filter(Project.id==project_id).first()
        if verify.is_deleted is True:
            logging.warning(f"project co id {project_id} da bi xoa")
            return 3
        qualify = db.query(Task).filter(Task.project_id==project_id).all()
        if not qualify:
            logging.warning(f"Khong tim thay task cua project co id {project_id}")
            return 2
        if keyword is None:
            information = db.query(Task).filter(Task.project_id==validation.project_id).all()
        else:
            keyword = keyword.lower()
            if keyword.isdigit():
                keyword= int(keyword)
            information = db.query(Task).filter(or_ (Task.assignee_id.ilike(f"%{keyword}%"),(Task.status.ilike(f"%{keyword}%")),(Task.priority.ilike(f"%{keyword}%")),(Task.title.ilike(f"%{keyword}%")))).all()
            if not information:
                logging.warning("Khong tim thay task co thong tin tuong tu")
                return 2
        logging.info(f"Da tim thay thong tin task")
        return information
    logging.warning(f"Nguoi dung co id {user_data["user_id"]} khong co quyen thuc hien xoa task theo keyword")
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail = "Khong du quyen truy cap chuc nang nay"
    )

file_types = ["jpg","png","pdf","docx"]

DIR_UPLOAD_FILE = "upload/files"
os.makedirs(DIR_UPLOAD_FILE,exist_ok=True)
def handle_upload_file(file:UploadFile = File(...)):
    type_file = file.filename.split(".")[-1]
    if type_file not in file_types:
        logging.warning(f"Loai file tai len khong hop le")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dinh dang file can la jpg,png,pdf hoac docx"
        )
    new_file_name = f"{uuid.uuid4().hex}.{type_file}"
    url_image_create = os.path.join(DIR_UPLOAD_FILE,new_file_name)

    with open(url_image_create,"wb") as buffer:
        shutil.copyfileobj(file.file,buffer)
    logging.info(f"Da them thanh cong file co ten {file.filename}")
    return file.filename

def upload_file(task_id:int ,db:Session = Depends,file:UploadFile = File(...),user_data:dict = Depends(handle_token)):
    validation = db.query(ProjectMember).filter(ProjectMember.user_id==user_data["user_id"]).first()
    if not validation:
        return None
    if validation.role=="member":
        information = db.query(Task).filter(Task.id==task_id).first()
        in_project = db.query(ProjectMember).filter(ProjectMember.user_id==user_data["user_id"],ProjectMember.project_id==information.project_id).all()
        if not in_project:
            logging.warning(f"Nguoi dung co id {user_data["user_id"]} khong co trong project")
            return 2
        if not information:
            logging.warning(f"Khong tim thay task co id {task_id}")
            return None
        information.attach_file = handle_upload_file(file)
        db.commit()
        db.refresh(information)
        logging.info(f"Da tem thanh cong file moi")
        return information
    logging.warning(f"Nguoi dung co id {user_data["user_id"]} khong co quyen thuc hien them file")
    raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Khong du quyen truy cap"
        )

