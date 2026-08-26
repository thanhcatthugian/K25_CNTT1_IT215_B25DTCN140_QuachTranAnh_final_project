from pydantic import BaseModel,Field,ConfigDict

class CreateProject(BaseModel):
    name : str = Field(...)
    description: str = Field(default = None)

class UpdateProject(BaseModel):
    name : str = Field(default = None)
    description: str = Field(default = None)

class ProjectResponse(BaseModel):
    id:int
    name:str
    description:str
    owner_id:int
    created_at: str
    is_deleted: bool
    model_config = ConfigDict(from_attributes=True)
    