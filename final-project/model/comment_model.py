from database import Base
from sqlalchemy import Column,Text,Integer,ForeignKey,Boolean
from sqlalchemy.orm import relationship
class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer,primary_key=True,autoincrement=True)
    comment_text = Column(Text)
    task_id = Column(Integer,ForeignKey("tasks.id"))
    task = relationship("Task",back_populates="comments")