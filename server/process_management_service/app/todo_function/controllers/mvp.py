from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.todo_function.models import MVP, Element
from app.todo_function.schemas import MVPCreate, MVPUpdate

def create_mvp(db: Session, mvp: MVPCreate):
    """Create a new MVP item attached to an element"""
    # Validate element exists
    element = db.query(Element).filter(Element.id == mvp.element_id).first()
    if not element:
        raise HTTPException(status_code=404, detail="Element not found")
    
    db_mvp = MVP(
        title=mvp.title,
        description=mvp.description,
        element_id=mvp.element_id,
        is_completed=False
    )
    db.add(db_mvp)
    db.commit()
    db.refresh(db_mvp)
    return db_mvp

def get_mvps(db: Session, skip: int = 0, limit: int = 100):
    """Get all MVP items with pagination"""
    return db.query(MVP).offset(skip).limit(limit).all()

def get_mvp(db: Session, mvp_id: int):
    """Get a single MVP item by ID"""
    return db.query(MVP).filter(MVP.id == mvp_id).first()

def get_mvps_by_element(db: Session, element_id: int):
    """Get all MVP items for a specific element"""
    return db.query(MVP).filter(MVP.element_id == element_id).all()

def update_mvp(db: Session, mvp_id: int, mvp_data: MVPUpdate):
    """Update MVP item (title, description, completion status)"""
    db_mvp = db.query(MVP).filter(MVP.id == mvp_id).first()
    if not db_mvp:
        return None
    
    if mvp_data.title is not None:
        db_mvp.title = mvp_data.title
    
    if mvp_data.description is not None:
        db_mvp.description = mvp_data.description
    
    if mvp_data.is_completed is not None:
        db_mvp.is_completed = mvp_data.is_completed
    
    db.commit()
    db.refresh(db_mvp)
    return db_mvp

def delete_mvp(db: Session, mvp_id: int):
    """Delete an MVP item"""
    db_mvp = db.query(MVP).filter(MVP.id == mvp_id).first()
    if not db_mvp:
        return None
    
    db.delete(db_mvp)
    db.commit()
    return db_mvp