from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.todo_function.core.database import Base

class Element(Base):
    __tablename__ = 'elements'

    id = Column(Integer, primary_key=True, index=True)
    
    # ✅ NEW: Link to the Project Management Service
    # We assume project_id is an Integer based on your previous Project Service code
    project_id = Column(Integer, nullable=False) 
    
    title = Column(String(255))
    description = Column(String)
    type = Column(String(50))

    tasks = relationship("Task", back_populates="element", cascade="all, delete-orphan")

    __mapper_args__ = {
        'polymorphic_identity': 'element',
        'polymorphic_on': type
    }