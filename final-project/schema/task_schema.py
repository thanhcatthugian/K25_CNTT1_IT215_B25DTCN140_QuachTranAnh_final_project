from pydantic import BaseModel,ConfigDict,Field
from typing import Literal
from datetime import datetime
class CreateTask(BaseModel):
    title:str = Field(...)
    description: str = Field(None)
    status: Literal["todo","in_progress","done"] = Field(...)
    priority : Literal["low","medium","high"]  = Field(...)
    due_date :str   = Field(...)
    assignee_id : int = Field(None)

class TaskResponse(BaseModel):
    id:int
    title :str
    description: str
    status: Literal["todo","in_progress","done"]
    priority : Literal["low","medium","high"]
    due_date:str
    created_at:str
    project_id: int
    assignee_id:int
    model_config = ConfigDict(from_attributes=True)