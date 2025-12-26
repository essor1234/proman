from sqlalchemy import Column, Integer, ForeignKey
from typing import TYPE_CHECKING

# Import the parent class
from .element import Element

# Only import Task for type hinting (prevents circular import errors at runtime)
if TYPE_CHECKING:
    from .task import Task

class Todo(Element):
    __tablename__ = 'todo'
    
    # 1. Primary Key must be Integer
    # 2. Must be a ForeignKey to the parent table 'elements.id'
    id = Column(Integer, ForeignKey('elements.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'todo',
    }

    # Methods from Class Diagram
    def add_task(self, task: "Task"):
        self.tasks.append(task)

    def delete_task(self, task_id: str):
        # Logic to remove task from list
        pass

    def update_task(self, task_id: str):
        # Logic to update task
        pass