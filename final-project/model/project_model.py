from database import Base
from sqlalchemy import Column,String,Integer,Text,DateTime,ForeignKey,Boolean
from sqlalchemy.orm import relationship
class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer,primary_key=True,autoincrement=True)
    name = Column(String(125),nullable=False)
    description = Column(Text)
    created_at = Column(DateTime,nullable=False)
    user = relationship("User",back_populates="projects")
    owner_id = Column(Integer,ForeignKey("users.id"),nullable=False)
    project_members = relationship("ProjectMember",back_populates="project")
    tasks = relationship("Task",back_populates="project")
    is_deleted = Column(Boolean,default=False,nullable=False)
