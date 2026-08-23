from database import *
from schema.user_schema import *
from model.user_model import *
from service.user_sevice import *
from fastapi import APIRouter,HTTPException,status,Depends,Request,Query
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

router = APIRouter(
    prefix="/users"
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


@router.get("/",dependencies=[Depends(RoleCheck(["admin"]))],status_code=status.HTTP_200_OK,tags=["Xem danh sach / Tim nguoi dung"],response_model=UserResponse)

def show_user(request:Request,keyword:str = Query(None),status_keyword:str = Query(None),db:Session  = Depends(get_db)):
    information = show_through_id(keyword,status_keyword,db)
    if information is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khong tim thay thong tin tuong ung"
        )
    return create_response(
        status_code=status.HTTP_200_OK,
        message="Lay thong tin thanh cong",
        data = jsonable_encoder(information),
        path = request.url.path
    )

@router.get("/me",status_code=status.HTTP_200_OK,tags=["Xem  ho so ca nhan"],response_model=UserResponse,dependencies=[Depends(RoleCheck(["user","admin"]))])

def check_current_account(request:Request,user_data: dict = Depends(SECURITY_KEY)):
    information = handle_token(user_data)
    return create_response(
        status_code=status.HTTP_200_OK,
        message="Lay thong tin thanh cong",
        data = jsonable_encoder(information),
        path = request.url.path
    )