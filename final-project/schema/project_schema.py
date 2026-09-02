from pydantic import BaseModel,Field,ConfigDict
from typing import Optional
class CreateProject(BaseModel):
    name : str = Field(...)
    description: str = Field(default = None)

class UpdateProject(BaseModel):
    name : Optional[str] = None
    description: Optional[str] = None

class ProjectResponse(BaseModel):
    id:int
    name:str
    description:str
    owner_id:int
    created_at: str
    is_deleted: bool
    model_config = ConfigDict(from_attributes=True)
    