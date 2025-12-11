from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.todo_function.models import Task, Element
from app.todo_function.schemas import TaskCreate, TaskUpdate



def create_task(db: Session, task: TaskCreate):
    # 1. Debug Print: Check what Python actually received
    print(f"DEBUG LOG: Received isFinished = {task.is_finished}") 

    # 2. Check Parent
    parent = db.query(Element).filter(Element.id == task.elements_id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent Element not found")

    # 3. Explicit Mapping
    db_task = Task(
        description=task.description,
        
   
        is_finished=task.is_finished,
        
        elements_id=task.elements_id
    )
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task
def update_task(db: Session, task_id: int, task_data: TaskUpdate):
    """
    Updates task details (description or finished status).
    """
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        return None
    
    if task_data.description is not None:
        db_task.description = task_data.description
        
    if task_data.is_finished is not None:
        db_task.is_finished = task_data.is_finished
        
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_element(db: Session, element_id: int):
    """
    Generic delete for Todo or Moscow (cascades to tasks).
    """
    db_element = db.query(Element).filter(Element.id == element_id).first()
    if not db_element:
        return None
    
    db.delete(db_element)
    db.commit()
    return db_element