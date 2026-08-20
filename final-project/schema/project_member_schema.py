from pydantic import BaseModel,Field,ConfigDict
from typing import Literal
class AddMember(BaseModel):
    user_id : int   = Field(...)
    role : Literal["owner","member"]  = Field(...)

class MemberResponse(BaseModel):
    project_id  : int
    user_id :int
    role : Literal["owner","member"]
    joined_at: str
    model_config = ConfigDict(from_attributes=True)

