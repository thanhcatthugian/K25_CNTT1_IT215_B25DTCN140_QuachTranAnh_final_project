from database import *
from schema.task_schema import *
from model.task_model import *
from service.task_service import *
from fastapi import APIRouter,HTTPException,status,Depends,Request,Path,UploadFile,File
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import os,uuid,shutil

router = APIRouter(
    prefix="/tasks"
)

def create_response(
        status_code:int,
        message: str,
        error =  None,
        data = None,
        path = ""
):
    return JSONResponse(
        status_code=status_code,
        content={
            "status_code":status_code,
            "message": message,
            "error": error,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "path": path
        }
    )



@router.get("/{task_id}",tags=["Lay chi tiet task"],status_code=status.HTTP_200_OK,response_model=TaskResponse,dependencies=[Depends(RoleCheck(["admin","user"]))])

def show_task_through_id(request:Request,task_id:int = Path(...),db:Session = Depends(get_db),user_data:dict = Depends(handle_token)):
    information = show_through_id(task_id,db,user_data)
    if information is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khong tim thay thong tin task"
        )
    return create_response(
        status_code=status.HTTP_200_OK,
        message="Lay thanh cong du lieu",
        data=jsonable_encoder(information),
        path = request.url.path
    )

@router.patch("/{task_id}",tags = ["Cap nhat task"],status_code=status.HTTP_200_OK,response_model=TaskResponse,dependencies=[Depends(RoleCheck(["admin","user"]))])

def update_task(request:Request,new_task: CreateTask,task_id:int = Path(...),db:Session = Depends(get_db),user_data:dict = Depends(handle_token)):
    information = update_task_information(task_id,db,new_task,user_data)
    if information is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khong tim thay thong tin task"
        )
    return create_response(
        status_code=status.HTTP_200_OK,
        message="Cap nhat thanh cong du lieu",
        data=jsonable_encoder(information),
        path = request.url.path
    )

@router.delete("/{task_id}",tags = ["Xoa task"],status_code=status.HTTP_200_OK,response_model=TaskResponse,dependencies=[Depends(RoleCheck(["admin","user"]))])

def update_task(request:Request,task_id:int = Path(...),db:Session = Depends(get_db),user_data:dict = Depends(handle_token)):
    information = remove_task_information(task_id,db,user_data)
    if information is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khong tim thay thong tin task"
        )
    return create_response(
        status_code=status.HTTP_200_OK,
        message="Xoa thanh cong du lieu",
        data=jsonable_encoder(information),
        path = request.url.path
    )

@router.post("/{task_id}/attachments",tags = ["Them file"],status_code=status.HTTP_200_OK,response_model=TaskResponse,dependencies=[Depends(RoleCheck(["admin","user"]))])

def upload_new_file(request:Request,file:UploadFile = File(...),task_id:int =Path(...),db:Session = Depends(get_db),user_data:dict = Depends(handle_token)):
    information = upload_file(task_id,db,file,user_data)
    if information is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khong tim thay thong tin task"
        )
    return create_response(
        status_code=status.HTTP_200_OK,
        message="Xoa thanh cong du lieu",
        data=jsonable_encoder(information),
        path = request.url.path
    )