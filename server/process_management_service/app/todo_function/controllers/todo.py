from sqlalchemy.orm import Session
from app.todo_function.models import Todo
from app.todo_function.schemas import TodoCreate

def create_todo(db: Session, todo: TodoCreate):
    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        project_id=todo.project_id
    )
    
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

# ✅ RESTORE THIS FUNCTION (The error was complaining about this)
def get_todos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Todo).offset(skip).limit(limit).all()

def get_todo(db: Session, todo_id: int):
    return db.query(Todo).filter(Todo.id == todo_id).first()

# Keep this useful new function for filtering by project
def get_todos_by_project(db: Session, project_id: int):
    return db.query(Todo).filter(Todo.project_id == project_id).all()