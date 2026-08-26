import time
from fastapi import HTTPException,status

login_attemps = {}

max_attemps = 5

lock_time = 60

def record_login(key:str):
    global login_attemps,max_attemps,lock_time
    current_time = time.time()
    if key not in login_attemps:
        login_attemps[key] = {"attemps": 1,"lock_until": 0}
    else:
        login_attemps[key]["attemps"]+=1
    if login_attemps[key]["attemps"]>=max_attemps:
        login_attemps[key]["lock_until"]+=lock_time+current_time


def clear_login(key:str):
    global login_attemps,max_attemps,lock_time
    if key in login_attemps:
        login_attemps = {}

def check_brute_force(key:str):
    global login_attemps,max_attemps,lock_time
    current_time = time.time()
    if key in login_attemps:
        record = login_attemps[key]
        if current_time < record["lock_until"]:
            remaining_time = int(record["lock_until"]-current_time)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail = f"Tai khoan bi khoa do dang nhap qua nhieu. Con {remaining_time} giay cho den khi dang nhap duoc"
            )
