from pydantic import BaseModel,Field
from typing import Optional
class CreateComment(BaseModel):
    comment_text:Optional[str] = Field(None,max_length=200)

class CommentResponse(BaseModel):
    id: int
    comment_text:str
    task_id: int