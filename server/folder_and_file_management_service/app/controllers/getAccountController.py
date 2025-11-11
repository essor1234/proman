from http.client import HTTPException
from sqlmodel import SQLModel, Field, Session, select


"""
Get account user details logic. -> add to create create_file_logic in file.py
"""
def get_account_user_logic(user_id: int, db: Session) -> dict:
    # Placeholder logic for retrieving account user details
    # Replace with actual database queries and logic as needed
    stmt = select(SQLModel).where(SQLModel.id == user_id)
    db_user = db.exec(stmt).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"id": db_user.id, "username": db_user.username, "email": db_user.email}


def get_project_id_logic(project_id: int, db: Session) -> dict:
    # Placeholder logic for retrieving project details
    # Replace with actual database queries and logic as needed
    stmt = select(SQLModel).where(SQLModel.id == project_id)
    db_project = db.exec(stmt).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return {"id": db_project.id, "name": db_project.name, "description": db_project.description}