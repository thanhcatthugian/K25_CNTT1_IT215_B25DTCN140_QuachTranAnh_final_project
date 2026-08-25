from pydantic import BaseModel,Field,ConfigDict
from typing import Literal
class AddMember(BaseModel):
    user_id : int   = Field(...)

class MemberResponse(BaseModel):
    project_id  : int
    user_id :int
    role : Literal["owner","member"]
    joined_at: str
    is_deleted:bool
    model_config = ConfigDict(from_attributes=True)

class AddManyMember(BaseModel):
    user_id : str  = Field(...)