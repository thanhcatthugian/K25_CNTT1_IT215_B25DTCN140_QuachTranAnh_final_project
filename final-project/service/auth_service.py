from schema.user_schema import CreateAccount,LogIn

from model.user_model import*
from sqlalchemy.orm import Session
from datetime import datetime
from utils import *
def add_account(new_account:CreateAccount,db:Session):
    information = db.query(User).filter(User.email==new_account.email).first()
    if information:
        return None
    verified_password = ground_password(new_account.password)
    totally_new = User(
        email = new_account.email,
        password_hash = verified_password,
        full_name= new_account.full_name,
        role = new_account.role,
        is_active = new_account.is_active,
        created_at = datetime.now()
    )
    db.add(totally_new)
    db.commit()
    db.refresh(totally_new)
    data_response = User(
        email = new_account.email,
        full_name= new_account.full_name,
        role = new_account.role,
        is_active = new_account.is_active,
        created_at = datetime.now().isoformat()
    )
    return data_response

def log_in_account(log_information:LogIn,db:Session):
    information = db.query(User).filter(User.email==log_information.email).first()
    if not information:
        return None
    is_correct = check_password(log_information.password,information.password_hash)
    if is_correct is False:
        return None
    payload = {
        "sub": information.email,
        "user_id": information.id,
        "role": information.role,
        "full_name": information.full_name,
        "is_active": information.is_active
    }
    token = create_access_token(payload)
    return {
        "access_token": token,
        "token_type": "bearer",
        "expire_at": 1800
    }

