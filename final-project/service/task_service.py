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
    qualify = db.query(Task).filter(Task.title==new_task.title,Task.project_id==information.id).first()
    if qualify:
        return 3
    if information.is_deleted is True:
        logging.warning(f"Project co id {project_id} da bi xoa")
        return 1
    validation = db.query(ProjectMember).filter(ProjectMember.user_id==user_data["user_id"],ProjectMember.project_id==project_id).first()
    if not validation:
        logging.warning(f"Nguoi dung co id {user_data["user_id"]} khong co trong project")
        return 2
    if new_task.due_date is None:
        duedate = datetime.now()+timedelta(days=3)
    else:
        duedate = new_task.due_date
        print(duedate)
        if duedate < datetime.now(timezone.utc)+timedelta(hours=1):
            return 4
    if new_task.assignee_id is None:
        asgin_id = user_data["user_id"]
    else:
        asgin_id = new_task.assignee_id
    if validation.role=="member" or validation.role == "owner":
        totally_new = Task(
            title = new_task.title,
            description = new_task.description,
            status = new_task.status,
            priority = new_task.priority,
            created_at = datetime.now(),
            due_date = duedate,
            project_id = project_id,
            assignee_id = asgin_id,
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
        if not information:
            logging.warning(f"Khong tim thay task co id {task_id}")
            return None
        in_project = db.query(ProjectMember).filter(ProjectMember.user_id==user_data["user_id"],ProjectMember.project_id==information.project_id).all()
        if not in_project:
            logging.warning(f"Nguoi dung co id {user_data["user_id"]} khong co trong project")
            return 2
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
    if  validation.role=="owner":
        information = db.query(Task).filter(Task.id==task_id).first()
        if not information:
            logging.warning(f"Khong tim thay task co id {task_id}")
            return None
        is_exist = db.query(Project).filter(Project.id==information.project_id).first()
        qualify = db.query(Task).filter(Task.title==new_task.title,Task.project_id!=is_exist.id).first()
        if qualify:
            return 5
        in_project = db.query(ProjectMember).filter(ProjectMember.user_id==user_data["user_id"],ProjectMember.project_id==information.project_id).all()
        if not in_project:
            logging.warning(f"Nguoi dung co id {user_data["user_id"]} khong co trong project")
            return 2
        data = new_task.model_dump(exclude_unset=True)
        qualify = db.query(ProjectMember).filter(ProjectMember.user_id==new_task.assignee_id,ProjectMember.project_id==information.project_id).first()
        if not qualify:
            logging.warning(f"Nguoi dung co id {new_task.assignee_id} khong thuoc du an")
            return 1
        if qualify.is_deleted is True:
            logging.warning(f"Nguoi dung co id {new_task.assignee_id} da bi xoa")
            return 4
        if information.is_deleted is True:
            logging.warning(f"Task co id {task_id} da bi xoa")
            return 3
        if new_task.due_date is None:
            duedate = datetime.now()+timedelta(days=3)
        else:
            duedate = new_task.due_date
            print(duedate)
            if duedate < datetime.now(timezone.utc)+timedelta(hours=1):
                return 6
        if new_task.status == "done":
            information.completed_at = datetime.now(timezone.utc)
        else:
            information.completed_at = None
        for key,value in data.items():
            setattr(information,key,value)
        db.commit()
        db.refresh(information)
        logging.info(f"da cap nhat thanh cong thong tin cho task co id {task_id}")
        return information
    else:
        is_asignee = db.query(Task).filter(Task.assignee_id==user_data["user_id"],Task.id==task_id).first()
        if is_asignee:
            if new_task.status:
                is_asignee.status = new_task.status
            else:
                is_asignee.status = is_asignee.status
            db.commit()
            db.refresh(is_asignee)
            return is_asignee
        if not is_asignee:
            return 7
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
    if information.status !="todo":
        return 3
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
    if validation.role == "member" or validation.role == "owner":
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
    if validation.role=="member" or validation.role == "owner":
        information = db.query(Task).filter(Task.id==task_id).first()
        in_project = db.query(ProjectMember).filter(ProjectMember.user_id==user_data["user_id"],ProjectMember.project_id==information.project_id).all()
        if not in_project:
            logging.warning(f"Nguoi dung co id {user_data["user_id"]} khong co trong project")
            return 2
        if not information:
            logging.warning(f"Khong tim thay task co id {task_id}")
            return None
        if information.is_deleted is True:
            logging.warning(f"task co id {task_id} da bi xoa")
            return 3
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



def limit_offsett(project_id:int,limit_data:int,offset_data:int,db:Session,user_data:dict = Depends(handle_token)):
    information = db.query(Project).filter(Project.id==project_id).first()
    if not information:
        return None
    validation = db.query(ProjectMember).filter(ProjectMember.user_id==user_data["user_id"],ProjectMember.project_id==project_id).first()
    if not validation:
        return 1
    if validation.role == "member" or validation.role == "owner":
        if limit_data is None and offset_data is None:
            qualify = db.query(Task).filter(Task.project_id==project_id).all()
            if not qualify:
                return 2
            return qualify
        elif limit_data is not None and offset_data is None:
            if limit_data >=20:
                limit_data = 20
            qualify = db.query(Task).order_by(Task.created_at).filter(Task.project_id==project_id).limit(limit_data).all()
            if not qualify:
                return 2
            return qualify
        elif limit_data is None and offset_data is not None:
            qualify = db.query(Task).order_by(Task.created_at).filter(Task.project_id==project_id).offset(offset_data).all()
            if not qualify:
                return 2
            return qualify
        elif limit_data is not None and offset_data is not None:
            if limit_data >=50:
                limit_data=50
            qualify = db.query(Task).order_by(Task.created_at).filter(Task.project_id==project_id).limit(limit_data).offset(offset_data).all()
            if not qualify:
                return 2
            return qualify
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail = "Khong du quyen han truy cap chuc nang nay"
    )


def sort_tasks_asc_by_created_at(project_id:int,db:Session,user_data:dict = Depends(handle_token)):
    information = db.query(Project).filter(Project.id==project_id).first()
    if not information:
        return None
    validation = db.query(ProjectMember).filter(ProjectMember.user_id==user_data["user_id"],ProjectMember.project_id==project_id).first()
    if not validation:
        return 1
    if validation.role == "member" or validation.role == "owner":
        qualify = db.query(Task).order_by(Task.created_at.asc()).filter(Task.project_id==project_id).all()
        if not qualify:
            return 2
        return qualify
    raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail = "Khong du quyen han truy cap chuc nang nay"
        )


def sort_tasks_desc_by_created_at(project_id:int,db:Session,user_data:dict = Depends(handle_token)):
    information = db.query(Project).filter(Project.id==project_id).first()
    if not information:
        return None
    validation = db.query(ProjectMember).filter(ProjectMember.user_id==user_data["user_id"],ProjectMember.project_id==project_id).first()
    if not validation:
        return 1
    if validation.role == "member" or validation.role == "owner":
        qualify = db.query(Task).order_by(Task.created_at.asc()).filter(Task.project_id==project_id).all()
        if not qualify:
            return 2
        return qualify
    raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail = "Khong du quyen han truy cap chuc nang nay"
        )

def count_done_tasks(project_id:int,db:Session,user_data:dict = Depends(handle_token)):
    information = db.query(Project).filter(Project.id==project_id).first()
    count_done = 0
    count_task = 0
    if not information:
        return 1
    validation = db.query(ProjectMember).filter(ProjectMember.user_id==user_data["user_id"],ProjectMember.project_id==project_id).first()
    if not validation:
        return 2
    if validation.role == "owner" or validation.role == "member":
        qualify = db.query(Task).filter(Task.project_id==project_id).all()
        for i in qualify:
            if i.status == "done":
                count_done+=1
            count_task+=1
        return {"total_tasks": count_task, "done_tasks": count_done}
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail = "Khong du quyen truy cap chuc nang nay"
    )

def show_my_asigned_task(project_id:int,db:Session,user_data:dict = Depends(handle_token)):
    information = db.query(Project).filter(Project.id==project_id).first()
    if not information:
        return 1
    validation = db.query(ProjectMember).filter(ProjectMember.user_id==user_data["user_id"],ProjectMember.project_id==project_id).first()
    if not validation:
        return 2
    if validation.role=="owner" or validation == "member":
        qualify = db.query(Task).filter(Task.project_id==project_id,Task.assignee_id==user_data["user_id"])
        if not qualify:
            return 3
        return qualify
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail = "Khong du quyen truy cap chuc nang nay"
    )


def check_over_deadline(project_id:int,db:Session,user_data:dict = Depends(handle_token)):
    information = db.query(Project).filter(Project.id==project_id).first()
    if not information:
        return 1
    validation = db.query(ProjectMember).filter(ProjectMember.user_id==user_data["user_id"],ProjectMember.project_id==project_id).first()
    if not validation:
        return 2
    if validation.role=="owner" or validation.role == "member":
        time_now = datetime.now(timezone.utc)
        qualify = db.query(Task).filter(Task.due_date<time_now,Task.status!="done",Task.project_id==project_id).all()
        if qualify:
            return qualify
        return 3
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail = "Nguoi dung khong du quyen thao tac chuc nang nay"
    )
    