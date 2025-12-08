from sqlalchemy.orm import Session
from fastapi import HTTPException

# Models
from app.todo_function.models import Todo, Moscow, Task, Element
# Schemas
from app.todo_function.schemas import (
    TodoCreate, TodoUpdate, 
    MoscowCreate, MoscowUpdate, 
    TaskCreate, TaskUpdate
)

import uuid

def create_task(db: Session, task: TaskCreate):
    """
    Creates a task attached to a generic Element (Todo or Moscow).
    """
    # 1. Validation: Check if Parent Element exists
    # We query 'Element' because it covers both Todo and Moscow tables
    parent = db.query(Element).filter(Element.id == task.elements_id).first()
    
    if not parent:
        # Match style of your create_project example (Raise HTTP exception in controller for validation failure)
        raise HTTPException(status_code=404, detail=f"Parent Element ID {task.elements_id} not found.")

    # 2. Create Task
    new_id = str(uuid.uuid4())
    db_task = Task(
        id=new_id,
        description=task.description,
        is_finished=task.isFinished,
        elements_id=task.elements_id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, task_id: str, task_data: TaskUpdate):
    """
    Updates task details (description or finished status).
    """
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        return None
    
    if task_data.description is not None:
        db_task.description = task_data.description
        
    if task_data.isFinished is not None:
        db_task.is_finished = task_data.isFinished
        
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_element(db: Session, element_id: str):
    """
    Generic delete for Todo or Moscow (cascades to tasks).
    """
    db_element = db.query(Element).filter(Element.id == element_id).first()
    if not db_element:
        return None
    
    db.delete(db_element)
    db.commit()
    return db_element