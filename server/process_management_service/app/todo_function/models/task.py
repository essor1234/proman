# app/todo_function/models/task.py

from sqlalchemy import Column, String, Boolean, ForeignKey, Integer
from sqlalchemy.orm import relationship
from ..core.database import Base

# Note: It is safe to import Element here for the ForeignKey if needed, 
# but for the relationship, using the string is safer.
from .element import Element 

class Task(Base):
    __tablename__ = 'task'

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    is_finished = Column(Boolean, default=False)
    
    # ForeignKey to the table name 'elements.id'
    elements_id = Column(Integer, ForeignKey('elements.id'))
    # ✅ CORRECT: Use the String "Element"
    element = relationship("Element", back_populates="tasks")