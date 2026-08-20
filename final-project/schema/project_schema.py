from pydantic import BaseModel,Field,ConfigDict

class CreateProject(BaseModel):
    name : str = Field(...)
    description: str = Field(None)
    owner_id : int = Field(...)

class ProjectResponse(BaseModel):
    id:int
    name:str
    description:str
    owner_id:str
    created_at: str
    model_config = ConfigDict(from_attributes=True)
    