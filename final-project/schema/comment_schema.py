from pydantic import BaseModel,Field

class CreateComment(BaseModel):
    comment_text:str = Field(default = None)

class CommentResponse(BaseModel):
    id: int
    comment_text:str
    task_id: int