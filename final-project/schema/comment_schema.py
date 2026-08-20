from pydantic import BaseModel,Field

class Comment(BaseModel):
    comment:str = Field(...,min_length=2)