from pydantic import BaseModel,ConfigDict,Field
from typing import Literal,Optional
from datetime import datetime
class CreateTask(BaseModel):
    title:str = Field(...,min_length=5,max_length=100)
    description: Optional[str] = Field(None,max_length=500)    
    status: Literal["todo","in_progress","done"] = Field(default="todo")
    priority : Literal["low","medium","high","urgent"]  = Field(default = "low")
    due_date :Optional[datetime] = None 
    assignee_id: Optional[int] = None

class UpdateTask(BaseModel):
    title:Optional[str] = Field(None,min_length=5,max_length=100)
    description: Optional[str] = Field(None,max_length=500)
    status: Optional[Literal["todo","in_progress","done"]] = None
    priority : Optional[Literal["low","medium","high","urgent"]] = None
    due_date : Optional[datetime] = None 
    assignee_id : Optional[int] = None

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
    