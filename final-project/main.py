from database import *
from fastapi import FastAPI,status,HTTPException,Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from datetime import datetime
import time
from router.auth_router import router as auth_router
from router.user_router import router as user_router
from router.project_member_router import router as project_member_router
from router.project_router import router as project_router
from router.task_router import router as task_router
from seed import *
app = FastAPI()
Base.metadata.create_all(bind = engine)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(project_router)
app.include_router(project_member_router)
app.include_router(task_router)
run_seed()
lst_org = [
    "http://localhost:3000/",
    "http://localhost:3001/"
    "http://localhost:8000/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=lst_org,
    allow_credentials=True,
    allow_methods=["*"]
)

@app.middleware("http")

async def calc_time_handler(request:Request,call_next):
    start_time = time.time()
    response = await call_next(request)
    end_time = time.time()-start_time
    print(end_time)
    return response


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

@app.exception_handler(RequestValidationError)

def request_validation_handler(request:Request,exc:RequestValidationError):
    return create_response(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        message="Loi dinh dang du lieu, vui long thu lai sau",
        error=exc.errors(),
        path = request.url.path
    )


@app.exception_handler(HTTPException)

def http_exception_handler(request:Request,exc:HTTPException):
    return create_response(
        status_code=exc.status_code,
        message=exc.detail,
        path = request.url.path
    )

@app.exception_handler(Exception)

def exception_handler(request:Request,exc:Exception):
    print(f"[INTERNAL SERVER ERROR] Path: {request.url.path} | {str(exc)}")
    return create_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="Server gap su co, vui long thu lai sau",
        path = request.url.path
    )

@app.get("/health-check",tags=["Kiem tra API"])

def health_check():
    return "Still good"


