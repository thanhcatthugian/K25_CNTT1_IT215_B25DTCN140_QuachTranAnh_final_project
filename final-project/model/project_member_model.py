from database import Base
from sqlalchemy import Column,Integer,Boolean,ForeignKey,Enum,DateTime
from sqlalchemy.orm import relationship
class ProjectMember(Base):
    __tablename__ = "project_members"
    project = relationship("Project",back_populates="project_members")
    user = relationship("User",back_populates="project_members")
    project_id = Column(Integer,ForeignKey("projects.id"),primary_key=True)
    user_id = Column(Integer,ForeignKey("users.id"),primary_key=True)
    role = Column(Enum("owner","member"),nullable=False)
    joined_at = Column(DateTime,nullable=False)
    is_deleted = Column(Boolean,default=False,nullable=False)