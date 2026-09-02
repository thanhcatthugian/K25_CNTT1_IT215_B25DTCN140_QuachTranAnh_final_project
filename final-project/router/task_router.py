from database import *
from schema.task_schema import *
from model.task_model import *
from service.task_service import *
from service.comment_service import *
from fastapi import APIRouter,HTTPException,status,Depends,Request,Query,Path,UploadFile,File
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

@router.get("{project_id}/limit-offset",tags = ["Phan trang theo ngay tao"],status_code=status.HTTP_200_OK,response_model=TaskResponse,dependencies=[Depends(RoleCheck(["admin","user"]))])

def task_page_pagnition(request:Request,limit_data: int = Query(default=5),offset_data:int = Query(None),project_id: int = Path(...),db:Session = Depends(get_db),user_data:dict = Depends(handle_token)):
    information = limit_offsett(project_id,limit_data,offset_data,db,user_data)
    if information is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "Khong tim thay project tuong ung"
        )
    elif information == 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail  = "Nguoi dung khong co trong du an"
        )
    elif information == 2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "Khong tim thay du lieu"
        )
    elif information == 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = "Task da ton tai"
        )
    elif information == 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = "Duedate can phai lon hon hien tai it nhat 1 tieng"
        )
    return create_response(
        status_code=status.HTTP_200_OK,
        message="Lay thanh cong thong tin",
        data=jsonable_encoder(information),
        path = request.url.path
    )
@router.get("/{project_id}/search",tags = ["Lay task theo keyword"],status_code=status.HTTP_200_OK,response_model=TaskResponse,dependencies=[Depends(RoleCheck(["admin","user"]))])

def search_task(request:Request,project_id:int = Path(...),keyword:str = Query(None),db:Session = Depends(get_db),user_data:dict = Depends(handle_token)):
    information = find_task_by_keyword(project_id,keyword,db,user_data)
    if information == 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nguoi dung khong co trong du an"
        )
    elif information == 2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "Khong tim thay thong tin tuong ung"
        )
    return create_response(
        status_code=status.HTTP_200_OK,
        message="Lay thanh cong du lieu",
        data=jsonable_encoder(information),
        path = request.url.path 
    )

@router.get("/{project_id}/tasks/count",tags = ["Xem tong quan task"],status_code=status.HTTP_200_OK,dependencies=[Depends(RoleCheck(["admin","user"]))])

def show_summary_of_task(request:Request,project_id:int = Path(...),db:Session = Depends(get_db),user_data:dict = Depends(handle_token)):
    information = count_done_tasks(project_id,db,user_data)
    if information == 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "Khong tim thay project tuong tu"
        )
    elif information ==2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail = "NGuoi dung khong ton tai trong project"
        )
    return create_response(
        status_code=status.HTTP_200_OK,
        message="Lay thanh cong thong tin tong qua cac task",
        data = jsonable_encoder(information),
        path = request.url.path
    )

@router.get("/{task_id}",tags=["Lay chi tiet task"],status_code=status.HTTP_200_OK,response_model=TaskResponse,dependencies=[Depends(RoleCheck(["admin","user"]))])

def show_task_through_id(request:Request,task_id:int = Path(...),db:Session = Depends(get_db),user_data:dict = Depends(handle_token)):
    information = show_through_id(task_id,db,user_data)
    if information is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khong tim thay thong tin task"
        )
    elif information == 2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail = "Khong the xem task ma nguoi dung khong thuoc du an"
        )
    return create_response(
        status_code=status.HTTP_200_OK,
        message="Lay thanh cong du lieu",
        data=jsonable_encoder(information),
        path = request.url.path
    )

@router.patch("/{task_id}",tags = ["Cap nhat task"],status_code=status.HTTP_200_OK,response_model=TaskResponse,dependencies=[Depends(RoleCheck(["admin","user"]))])

def update_task(request:Request,new_task: UpdateTask,task_id:int = Path(...),db:Session = Depends(get_db),user_data:dict = Depends(handle_token)):
    information = update_task_information(task_id,db,new_task,user_data)
    if information is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khong tim thay thong tin task"
        )
    elif information == 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail= "Thanh vien khong thuoc du an"
        )
    elif information == 2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail = "Khong the chinh sua task ma nguoi dung khong thuoc du an"
        )
    elif information == 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task da bi xoa"
        )
    elif information == 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = "Thanh vien phu trach khong ton tai"
        )
    elif information == 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = "Task da ton tai"
        )
    elif information == 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = "Duedate can phai lon hon hien tai it nhat 1 tieng"
        )
    elif information == 7:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "Khong tim thay task duoc giao"
        )
    return create_response(
        status_code=status.HTTP_200_OK,
        message="Cap nhat thanh cong du lieu",
        data=jsonable_encoder(information),
        path = request.url.path
    )

@router.delete("/{task_id}",tags = ["Xoa task"],status_code=status.HTTP_204_NO_CONTENT,dependencies=[Depends(RoleCheck(["admin","user"]))])

def remove_task(request:Request,task_id:int = Path(...),db:Session = Depends(get_db),user_data:dict = Depends(handle_token)):
    information = soft_delete_task(task_id,db,user_data)
    if information is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khong tim thay thong tin task"
        )
    elif information == 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail = "Khong the chinh sua task ma nguoi dung khong thuoc du an"
        )
    elif information == 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = "Task da bi xoa"
        )
    
    elif information==3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = "Chi co the xoa task o trang thai todo"
        )
    
@router.get("/{project_id}/sort_asc",tags = ["Sap xep tang dan theo ngay tao task"],status_code=status.HTTP_200_OK,response_model=TaskResponse,dependencies=[Depends(RoleCheck(["admin","user"]))])

def sort_by_asc(request:Request,project_id: int = Path(...),db:Session = Depends(get_db),user_data:dict = Depends(handle_token)):
    information = sort_tasks_asc_by_created_at(project_id,db,user_data)
    if information is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "Khong tim thay project nay"
        )
    elif information == 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nguoi dung khong thuoc du an"
        )
    elif information == 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = "Khong tim thay task cua project nay"
        )
    return create_response(
            status_code=status.HTTP_200_OK,
            message="Sap xep thanh cong du lieu",
            data=jsonable_encoder(information),
            path = request.url.path
        )

@router.get("/{project_id}/sort_desc",tags = ["Sap xep giam dan theo ngay tao task"],status_code=status.HTTP_200_OK,response_model=TaskResponse,dependencies=[Depends(RoleCheck(["admin","user"]))])

def sort_by_desc(request:Request,project_id: int = Path(...),db:Session = Depends(get_db),user_data:dict = Depends(handle_token)):
    information = sort_tasks_desc_by_created_at(project_id,db,user_data)
    if information is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "Khong tim thay project nay"
        )
    elif information == 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nguoi dung khong thuoc du an"
        )
    elif information == 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = "Khong tim thay task cua project nay"
        )
    return create_response(
            status_code=status.HTTP_200_OK,
            message="Sap xep thanh cong du lieu",
            data=jsonable_encoder(information),
            path = request.url.path
        )
@router.get("/{project_id}/sorting/over-deadline",status_code=status.HTTP_200_OK,tags = ["Tim kiem task qua han theo project"],dependencies=[Depends(RoleCheck(["admin","user"]))],response_model=TaskResponse)
def check_deadline(request:Request,project_id:int = Path(...),db:Session = Depends(get_db),user_data:dict = Depends(handle_token)):
    information = check_over_deadline(project_id,db,user_data)
    if information==1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khong tim thay project"
        )
    elif information==2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,

            detail="Nguoi dung khong thuoc project"
        )
    elif information==3:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "Khong co task nao qua han"
        )
    return create_response(
        status_code=status.HTTP_200_OK,
        message="lay thanh cong du lieu",
        data=jsonable_encoder(information),
        path = request.url.path
    )

@router.get("/{project_id}/my-asigned-tasks",status_code=status.HTTP_200_OK,tags = ["Xem task duoc giao cua nguoi dung theo project"],response_model=TaskResponse,dependencies=[Depends(RoleCheck(["admin","user"]))])
def show_my_asigned(request:Request,project_id:int = Path(...),db:Session = Depends(get_db),user_data: dict = Depends(handle_token)):
    information = show_my_asigned_task(project_id,db,user_data)
    if information==1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khong tim thay project"
        )
    elif information==2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,

            detail="Nguoi dung khong thuoc project"
        )
    elif information==3:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "Khong co task nao duoc giao"
        )
    return create_response(
            status_code=status.HTTP_200_OK,
            message="lay thanh cong du lieu",
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
    elif information == 2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail = "Khong the them file ma nguoi dung khong thuoc du an"
        )
    elif information == 3:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail = "Du an da bi xoa"
        )
    return create_response(
        status_code=status.HTTP_200_OK,
        message="Xoa thanh cong du lieu",
        data=jsonable_encoder(information),
        path = request.url.path
    )

@router.post("/{task_id}/comments",tags = ["Them comment"],status_code=status.HTTP_201_CREATED,response_model=CommentResponse,dependencies=[Depends(RoleCheck(["admin","user"]))])

def post_comment(request:Request,new_comment:CreateComment,task_id:int = Path(...),db:Session = Depends(get_db),user_data:dict = Depends(handle_token)):
    information = add_comment(task_id,new_comment,db,user_data)
    if information == 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = "Task da bi xoa"
        )
    elif information == 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = "Memeber da bi xoa"
        )
    elif information == 4:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail = "Nguoi dung khong co trong du an"
        )
    elif information == 5:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "Khong tim thay thong tin task"
        )
    return create_response(
        status_code=status.HTTP_201_CREATED,
        message="Them thanh cong comment",
        data=jsonable_encoder(information),
        path = request.url.path
    )
