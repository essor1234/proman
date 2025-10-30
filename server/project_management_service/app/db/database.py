from typing import Optional
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine= create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

sessionLocal= sessionmaker(autocommit=False, autoflush=False,bind=engine)

Base = declarative_base()


def get_db():
    db=sessionLocal()
    try:
        yield db
    finally:
        db.close()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email=Column(String, index=True)

    #A user can be in many groups, accessed via the UserGroup table
    groups = relationship("UserGroup", back_populates="user")

    #A user can be in many projects, accessed via the ProjectMember table
    projects = relationship("ProjectMember", back_populates="user")

class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index= True)
    name = Column(String, index= True)
    # A group has many users, accessed via the UserGroup table
    users = relationship("UserGroup", back_populates="group")
    # A group can have many projects (one-to-many)
    projects = relationship("Project", back_populates="group")

class UserGroup(Base):
    __tablename__ = "user_groups"

    userId = Column(Integer, ForeignKey("users.id"), primary_key=True) #
    groupId = Column(Integer, ForeignKey("groups.id"), primary_key=True)#
    role = Column(String, default="member", index=True)
    
    # relationships to the "parent" tables
    user = relationship("User", back_populates="groups")
    group = relationship("Group", back_populates="users")

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer,primary_key=True, index= True)
    name = Column(String, index= True)
    groupId = Column(Integer, ForeignKey("groups.id"), index= True)

    # relationship to access the parent Group object
    group = relationship("Group", back_populates="projects")
    
    # A project has many members, accessed via the ProjectMember table
    members = relationship("ProjectMember", back_populates="project")



class ProjectMember(Base):
    __tablename__ = "project_members"

    userId = Column(Integer, ForeignKey("users.id"), primary_key=True)#
    projectId = Column(Integer, ForeignKey("projects.id"), primary_key=True)#
    role = Column(String,default="member", index=True)

    user = relationship("User", back_populates="projects")
    project = relationship("Project", back_populates="members")


