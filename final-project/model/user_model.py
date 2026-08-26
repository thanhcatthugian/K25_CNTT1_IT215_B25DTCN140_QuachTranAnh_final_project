from database import Base
from sqlalchemy import Column,String,Integer,Enum,Boolean,DateTime
from sqlalchemy.orm import relationship
class User(Base):
    __tablename__ = "users"

    id = Column(Integer,primary_key=True,autoincrement=True)
    email = Column(String(125),nullable=False,unique=True)
    password_hash = Column(String(255),nullable=False)
    full_name = Column(String(125),nullable=False)
    role = Column(Enum("user","admin"),default="user",nullable=False)
    is_active = Column(Boolean,nullable=False,default= True)
    created_at = Column(DateTime,nullable=False)
    

    projects = relationship("Project",back_populates="user")
    project_members = relationship("ProjectMember",back_populates="user")
    tasks = relationship("Task",back_populates="user")
