from pydantic import BaseModel,ConfigDict,Field
from typing import Literal

class CreateTask(BaseModel):
    title:str = Field(...)
    description: str = Field(None)
    status: Literal["todo","in_progress","done"] = Field(default="todo")
    priority : Literal["low","medium","high"]  = Field(default = "low")
    due_date :str   = Field(...)

class UpdateTask(BaseModel):
    title:str = Field(...)
    description: str = Field(None)
    status: Literal["todo","in_progress","done"] = Field(default="todo")
    priority : Literal["low","medium","high"]  = Field(default = "low")
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
    is_deleted:bool
    model_config = ConfigDict(from_attributes=True)
    