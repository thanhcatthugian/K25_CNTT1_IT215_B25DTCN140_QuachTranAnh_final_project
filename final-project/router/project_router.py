from database import *
from schema.project_schema import *
from model.project_model import *
from service.project_service import *
from fastapi import APIRouter,HTTPException,status,Depends,Request,Path,Query
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Literal
from schema.project_member_schema import *
from service.project_member_service import get_information_by_role
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



@router.post("/",tags = ["Tao du an"],status_code=status.HTTP_201_CREATED,response_model=ProjectResponse,dependencies=[Depends(RoleCheck(["user","admin"]))])

def add_new_project(request:Request,new_project:CreateProject,user_data:dict = Depends(handle_token),db:Session = Depends(get_db)):
    information = add_project(new_project,db,user_data)
    if information == 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail= "Project da ton tai"
        )
    elif information == 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = "Nguoi dung da so huu du 5 du an voi vai tro owner"
        )
    return create_response(
        status_code=status.HTTP_201_CREATED,
        message="Tao thanh cong du an moi",
        data=jsonable_encoder(information),
        path = request.url.path
    )

@router.get("/",tags=["Lay thong tin du an dua tren role"],status_code=status.HTTP_200_OK,dependencies=[Depends(RoleCheck(["admin","user"]))],response_model=MemberResponse)

def check_through_role(request:Request,role_name:Literal["owner","member"] = Query(...),db:Session = Depends(get_db),user_data: dict = Depends(handle_token)):
    information = get_information_by_role(role_name,db,user_data)
    if information == 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "Khong tim thay nguoi dung trong du an nao co role tuong tu"
        )
    return create_response(
        status_code=status.HTTP_200_OK,
        message="Lay thanh cong thong tin",
        data=jsonable_encoder(information),
        path = request.url.path 
    )

@router.get("/",tags=["Danh sach du an cua toi"],status_code=status.HTTP_200_OK,response_model=ProjectResponse,dependencies=[Depends(RoleCheck(["user","admin"]))])

def show_my_project(request:Request,keyword:str = Query(None),db:Session = Depends(get_db),user_data:dict = Depends(handle_token)):
    information = show_own_project(db,keyword,user_data)
    if information is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "Nguoi dung chua co du an nao"
        )
    elif information ==1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nguoi dung khong ton tai trong du an"
        )
    return create_response(
        status_code=status.HTTP_200_OK,
        message="Lay thanh cong du an",
        data=jsonable_encoder(information),
        path = request.url.path
    )


@router.get("/{project_id}",tags=["Chi tiet du an"],status_code=status.HTTP_200_OK,response_model=ProjectResponse,dependencies=[Depends(RoleCheck(["admin","user"]))])

def show_project_through_id(request:Request,project_id: int = Path(...),user_data:dict = Depends(handle_token),db:Session = Depends(get_db)):
    information  = show_through_id(project_id,db,user_data)
    if information is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "Khong tim thay du an tuong ung"
        )
    elif information == 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "Khong tim thay project"
        )
    return create_response(
            status_code=status.HTTP_200_OK,
            message="Lay thanh cong du an",
            data=jsonable_encoder(information),
            path = request.url.path
        )

@router.patch("/{project_id}",tags = ["Cap nhat du an"],status_code=status.HTTP_200_OK,response_model=ProjectResponse,dependencies=[Depends(RoleCheck(["admin","user"]))])

def update_project(request:Request,new_project:UpdateProject,project_id:int = Path(...),user_data:dict = Depends(handle_token),db:Session = Depends(get_db)):
    information = update_information(project_id,new_project,db,user_data)
    if information is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "Khong tim thay du an tuong ung"
        )
    if information==1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail = "Khong the thao tac tren project"
        )
    elif information==2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = "Khong the thao tac tren du lieu da bi xoa"
        )
    elif information == 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail= "Project da ton tai"
        )
    return create_response(
        status_code=status.HTTP_200_OK,
        message="Cap nhat thanh cong du an",
        data=jsonable_encoder(information),
        path = request.url.path
    )

@router.delete("/{project_id}",tags=["Xoa du an"],status_code=status.HTTP_204_NO_CONTENT,dependencies=[Depends(RoleCheck(["admin","user"]))])

def remove_project(request:Request,project_id:int = Path(...),user_data:dict = Depends(handle_token),db:Session = Depends(get_db)):
    information = soft_delete_project(project_id,db,user_data)
    if information is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "Khong tim thay du an tuong ung"
        )
    if information==1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail = "Khong the thao tac tren project"
        )
    elif information==2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = "Project da duoc xoa"
        )
    elif information == 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = "Can xoa bot thanh vien truoc khi xoa du an"
        )

