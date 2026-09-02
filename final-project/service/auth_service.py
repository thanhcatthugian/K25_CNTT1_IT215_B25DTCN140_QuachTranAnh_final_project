from schema.user_schema import CreateAccount,LogIn
from setting import settings
from model.user_model import*
from sqlalchemy.orm import Session
from datetime import datetime
from utils import *
from fastapi import HTTPException,status

import logging

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format= "%(asctime)s + %(levelname)s + %(message)s",
    encoding="utf-8"
)


def add_account(new_account:CreateAccount,db:Session):
    count_upper = 0
    count_lower = 0
    count_number = 0
    count_symbol = 0
    information = db.query(User).filter(User.email==new_account.email).first()
    if information:
        logging.warning(f"Tai khoan co email {new_account.email} da ton tai")
        return None
    
    if len(new_account.password) <8:
        return 1
    for i in new_account.password:
        if i.isupper() and i.isalpha():
            count_upper+=1
        elif i.islower()and i.isalpha():
            count_lower +=1
        elif i.isdigit():
            count_number+=1
        elif not i.isalnum():
            count_symbol+=1
    if count_symbol == 0 or count_upper ==0 or count_lower == 0 or count_number ==0:
        return 2
    check_name = new_account.full_name.strip().split(" ")
    if len(check_name)<2:
        return 3
    verified_password = ground_password(new_account.password)
    totally_new = User(
        email = new_account.email.strip().lower(),
        password_hash = verified_password,
        full_name= new_account.full_name.strip(),
        role = "user",
        is_active = True,
        created_at = datetime.now()
    )
    db.add(totally_new)
    db.commit()
    db.refresh(totally_new)
    data_response = User(
        email = new_account.email.strip().lower(),
        full_name= new_account.full_name,
        role = "user",
    )
    logging.info(f"Tao thanh cong tai khoan moi co id {totally_new.id} ")
    return data_response

def log_in_account(log_information:LogIn,db:Session):
    information = db.query(User).filter(User.email==log_information.email).first()
    check_brute_force(log_information.email)
    if not information:
        logging.warning(f"Khong ton tai user co email {information.email}")
        record_login(log_information.email)
        return None
    is_correct = check_password(log_information.password,information.password_hash)
    if is_correct is False:
        logging.warning("Mat khau duoc nhap vao khong dung")
        record_login(log_information.email)
        return None
    if information.is_active is False:
        logging.warning("Tai khoan duoc dang nhap da ngung hoat dong")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tai khoan da ngung hoat dong"
        )
    clear_login(log_information.email)
    payload = {
        "sub": information.email,
        "user_id": information.id,
        "role": information.role,
        "full_name": information.full_name,
        "is_active": information.is_active
    }
    token = create_access_token(payload)
    logging.info("Da tao thanh cong mot access token moi")
    return {
        "access_token": token,
        "token_type": "bearer",
        "expire_at": settings.expired_time*60
    }

