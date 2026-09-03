from database import *
from schema.project_member_schema import *
from model.project_member_model import *
from service.project_member_service import *
from fastapi import APIRouter,HTTPException,status,Depends,Request,Path,Query
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from schema.task_schema import *
from service.task_service import *
router = APIRouter(
    prefix="/projects"
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


@router.post("/{project_id}/many-members",tags=["Them nhieu thanh vien du an"],status_code=status.HTTP_201_CREATED,response_model=MemberResponse,dependencies=[Depends(RoleCheck(["admin","user"]))])
def add_manh_new_member(request:Request,new_project_member:AddManyMember,project_id:int = Path(...),user_data:dict = Depends(handle_token),db:Session = Depends(get_db)):
    information = add_many_member(project_id,new_project_member,db,user_data)
    if information == 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail  = "khong the thao tac tren du an nay"
        )
    elif information is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khong tim thay du an tuong ung"
        )
    elif information == 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail= "Du an nay da bi xoa"
        )
    elif information == 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = "Du an da co du 10 thanh vien tham gia"
        )
    return create_response(
            status_code=status.HTTP_201_CREATED,
            message="Them thanh cong thanh vien moi",
            data=jsonable_encoder(information),
            path = request.url.path
        )

@router.post("/{project_id}/members",tags=["Them thanh vien du an"],status_code=status.HTTP_201_CREATED,response_model=MemberResponse,dependencies=[Depends(RoleCheck(["admin","user"]))])

def add_new_member(request:Request,new_project_member:AddMember,project_id:int = Path(...),user_data:dict = Depends(handle_token),db:Session = Depends(get_db)):
    information = add_project_memeber(project_id,new_project_member,db,user_data)
    if information is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khong tim thay du an tuong ung"
        )
    elif information == 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khong tim thay thong tin user"
        )
    elif information == 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = "Thanh vien da co trong du an nay"
        )
    elif information == 3:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail  = "khong the thao tac tren du an nay"
        )
    elif information == 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail= "Du an nay da bi xoa"
        )
    elif information ==5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = "User khong con hoat dong"
        )
    elif information == 6:
        return create_response(
            status_code=status.HTTP_200_OK,
            message="Thanh vien da duoc hoi sinh",
            path = request.url.path
        )
    elif information == 7:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = "Du an da co du 10 thanh vien tham gia"
        )
    return create_response(
        status_code=status.HTTP_201_CREATED,
        message="Them thanh cong thanh vien moi",
        data=jsonable_encoder(information),
        path = request.url.path
    )


@router.get("/{project_id}/members",tags = ["Xem danh sach thanh vien"],status_code=status.HTTP_200_OK,response_model=MemberResponse,dependencies=[Depends(RoleCheck(["admin","user"]))])

def get_member_list(request:Request,project_id:int = Path(...),user_data:dict = Depends(handle_token),db:Session = Depends(get_db)):
    information = show_member_list(project_id,db,user_data)
    if information is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khong tim thay thong tin du an"
        )
    elif information == 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail = "Khong the xem thanh vien du an ma nguoi dung khong thuoc du an"
        )
    return create_response(
        status_code=status.HTTP_200_OK,
        message="Lay thanh cong du lieu",
        data=jsonable_encoder(information),
        path = request.url.path
    )

@router.post("/{project_id}/tasks",tags=["Tao task"],status_code=status.HTTP_201_CREATED,response_model=TaskResponse,dependencies=[Depends(RoleCheck(["admin","user"]))])

def add_new_task(request:Request,new_task:CreateTask,project_id:int = Path(...),db:Session = Depends(get_db),user_data:dict = Depends(handle_token)):
    information = add_task(project_id,new_task,db,user_data)
    if information is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khong tim thay du an"
        )
    elif information ==1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = "Du an da bi xoa"
        )
    elif information == 2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail = "Khong the them task ma nguoi dung khong thuoc du an"
        )
    elif information == 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task da ton tai"
        )
    return create_response(
        status_code=status.HTTP_201_CREATED,
        message="Tao thanh cong task moi",
        data=jsonable_encoder(information),
        path = request.url.path
    )

@router.get("/{project_id}/tasks",tags=["Hien thi toan bo task theo project"],status_code=status.HTTP_200_OK,response_model=TaskResponse,dependencies=[Depends(RoleCheck(["admin","user"]))])

def show_all_task(request:Request,project_id:int = Path(...),db:Session = Depends(get_db),user_data:dict = Depends(handle_token)):
    information = show_tasks(project_id,db,user_data)
    if information is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khong tim thay du an lien quan"
        )
    elif information == 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail = "Khong the xem task ma nguoi dung khong thuoc du an"
        )
    elif information == 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = "Du an da bi xoa"
        )
    return create_response(
        status_code=status.HTTP_200_OK,
        message="Lay thanh cong du lieu",
        data=jsonable_encoder(information),
        path = request.url.path
    )
    
@router.delete("/{project_id}/members/{user_id}",tags = ["Xoa thanh vien"],status_code=status.HTTP_204_NO_CONTENT,dependencies=[Depends(RoleCheck(["admin","user"]))])

def remove_member(request:Request,project_id:int = Path(...),user_id:int = Path(...),user_data:dict = Depends(handle_token),db:Session = Depends(get_db)):
    information = soft_delete_member(project_id,user_id,db,user_data)
    if information is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "Khong tim thay thong tin project"
        )
    if information == 3:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khong tim thay thong tin thanh vien"
        )
    elif information == 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail = "Khong the xoa thanh vien du an ma nguoi dung khong thuoc du an"
        )
    elif information == 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = "Thanh vien nay da bi xoa"
        )
    elif information == 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = "Khong the xoa owner khoi du an"
        )


