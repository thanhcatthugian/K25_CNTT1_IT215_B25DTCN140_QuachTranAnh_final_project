from database import *
from schema.user_schema import *
from model.user_model import *
from service.auth_service import *
from fastapi import APIRouter,HTTPException,status,Depends,Request
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse



router = APIRouter(
    prefix="/auth"
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

@router.post("/register",tags=["Tao tai khoan"],status_code=status.HTTP_201_CREATED,response_model=UserResponse)

def register_account(request:Request,new_account:CreateAccount,db:Session = Depends(get_db)):
    information = add_account(new_account,db)
    if information is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tai khoan da ton tai"
        )
    if information == 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail = "Password can co do dai it nhat la 8"
        )
    elif information ==2:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail = "Mat khau can chua it nhat mot chu hoa,mot chu thuong, mot so va mot ky tu dac biet"
        )
    elif information == 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ten can chua it nhat 2 tu"
        )
    return create_response(
        status_code=status.HTTP_201_CREATED,
        message="Tao thanh cong tai khoan moi",
        data = jsonable_encoder(information),
        path = request.url.path
    )


@router.post("/login",tags=["Dang nhap"],status_code=status.HTTP_200_OK)

def log_in(request:Request,log_information:LogIn,db:Session = Depends(get_db)):
    information = log_in_account(log_information,db)
    if information is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mat khau hoac tai khoan sai"
        )
    return create_response(
        status_code=status.HTTP_200_OK,
        message="Dang nhap thanh cong tai khoan",
        data = jsonable_encoder(information),
        path = request.url.path
    )



