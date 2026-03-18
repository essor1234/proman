from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.todo_function.models import Note, Element
from app.todo_function.schemas import NoteCreate, NoteUpdate

def create_note(db: Session, note: NoteCreate):
    """Create a new note attached to an element"""
    # Validate element exists
    element = db.query(Element).filter(Element.id == note.element_id).first()
    if not element:
        raise HTTPException(status_code=404, detail="Element not found")
    
    db_note = Note(
        content=note.content,
        element_id=note.element_id
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

def get_notes(db: Session, skip: int = 0, limit: int = 100):
    """Get all notes with pagination"""
    return db.query(Note).offset(skip).limit(limit).all()

def get_note(db: Session, note_id: int):
    """Get a single note by ID"""
    return db.query(Note).filter(Note.id == note_id).first()

def get_notes_by_element(db: Session, element_id: int):
    """Get all notes for a specific element"""
    return db.query(Note).filter(Note.element_id == element_id).all()

def update_note(db: Session, note_id: int, note_data: NoteUpdate):
    """Update note content"""
    db_note = db.query(Note).filter(Note.id == note_id).first()
    if not db_note:
        return None
    
    if note_data.content is not None:
        db_note.content = note_data.content
    
    db.commit()
    db.refresh(db_note)
    return db_note

def delete_note(db: Session, note_id: int):
    """Delete a note"""
    db_note = db.query(Note).filter(Note.id == note_id).first()
    if not db_note:
        return None
    
    db.delete(db_note)
    db.commit()
    return db_note