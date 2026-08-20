from utils import *
from database import *
from datetime import datetime
from model.user_model import *
def run_seed():
    db = LocalSession()
    try:
        information = db.query(User).filter(User.email=="admin@gmail.com").first()
        if not information:
            admin_account = User(
                email = "admin@gmail.com",
                password_hash = ground_password("12345678"),
                full_name = "nigga",
                role = "admin",
                is_active = True,
                created_at = datetime.now()
            )
            db.add(admin_account)
            db.commit()
            db.refresh(admin_account)
            print("Da tao thanh cong tai khoan admin")
        else:
            print("Tai khoan admin da ton tai")
    except Exception:
        print("Khong tao duoc tai khoan admin")
    finally:
        db.close()

