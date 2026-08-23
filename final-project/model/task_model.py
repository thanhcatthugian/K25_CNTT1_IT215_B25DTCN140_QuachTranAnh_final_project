from database import Base
from sqlalchemy import Column,Integer,String,Text,Enum,DateTime,ForeignKey,Boolean
from sqlalchemy.orm import relationship
class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer,primary_key=True,autoincrement=True)
    title = Column(String(255),nullable=False)  
    description = Column(Text)
    status = Column(Enum("todo","in_progress","done"),nullable=False)
    priority = Column(Enum("low","medium","high"),nullable=False)
    due_date = Column(DateTime)
    created_at = Column(DateTime,nullable=False)
    user = relationship("User",back_populates="tasks")
    project = relationship("Project",back_populates="tasks")
    comments = relationship("Comment",back_populates="task")
    project_id = Column(Integer,ForeignKey("projects.id"),nullable=False)
    assignee_id = Column(Integer,ForeignKey("users.id"))
    attach_file = Column(String(255))
    is_deleted = Column(Boolean,default=False,nullable=False)



