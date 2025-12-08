from sqlalchemy import Column, String, Boolean, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship, Session
from .element import Element
from .task import Task
from ..core.database import Base
Base = declarative_base()   

class Todo(Element):
    """
    Class corresponding to 'TODO'.
    Inherits attributes from Element.
    """
    __tablename__ = 'todo'
    
    # The Primary Key is also the Foreign Key to Elements
    id = Column(String(50), ForeignKey('elements.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'todo',
    }

    # Methods from Class Diagram
    def add_task(self, task: Task):
        self.tasks.append(task)

    def delete_task(self, task_id: str):
        # Logic to remove task from list
        pass

    def update_task(self, task_id: str):
        # Logic to update task
        pass