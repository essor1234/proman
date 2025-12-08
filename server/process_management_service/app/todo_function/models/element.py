# app/todo_function/models/element.py

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from ..core.database import Base

class Element(Base):
    __tablename__ = 'elements'

    id = Column(String(50), primary_key=True)
    title = Column(String(255))
    description = Column(String)
    type = Column(String(50))

    # ✅ CORRECT: Use the String "Task", do NOT import the class Task here
    tasks = relationship("Task", back_populates="element", cascade="all, delete-orphan")

    __mapper_args__ = {
        'polymorphic_identity': 'element',
        'polymorphic_on': type
    }