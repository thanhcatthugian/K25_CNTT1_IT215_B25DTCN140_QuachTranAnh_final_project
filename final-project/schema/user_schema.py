from pydantic import BaseModel,Field,ConfigDict,EmailStr
from typing import Literal
class CreateAccount(BaseModel):
    email:EmailStr = Field(...)
    password:str = Field(...,min_length=8)
    full_name: str= Field(...)
    is_active : bool = Field(default=True)

class LogIn(BaseModel):
    email:EmailStr 
    password : str

class UserResponse(BaseModel):
    email :EmailStr
    full_name: str
    role: Literal["user","admin"]
    is_active : bool
    created_at: str
    model_config = ConfigDict(from_attributes=True)