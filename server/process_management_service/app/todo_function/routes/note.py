from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.todo_function.core.database import get_db
from app.todo_function.core.security import get_current_user
from app.todo_function.schemas import Note as NoteSchema, NoteCreate, NoteUpdate
from app.todo_function.controllers import (
    create_note, get_notes, get_note, get_notes_by_element, update_note, delete_note
)

router = APIRouter(prefix="/process", tags=["Notes"])

@router.post("/notes/", response_model=NoteSchema, status_code=status.HTTP_201_CREATED)
def create_new_note(
    note: NoteCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new note attached to an element"""
    return create_note(db, note)

@router.get("/notes/", response_model=List[NoteSchema])
def read_all_notes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all notes with pagination"""
    return get_notes(db, skip=skip, limit=limit)

@router.get("/notes/{note_id}", response_model=NoteSchema)
def read_one_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a single note by ID"""
    note = get_note(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@router.get("/elements/{element_id}/notes/", response_model=List[NoteSchema])
def read_notes_by_element(
    element_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all notes for a specific element"""
    return get_notes_by_element(db, element_id)

@router.put("/notes/{note_id}", response_model=NoteSchema)
def update_existing_note(
    note_id: int,
    note_update: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a note"""
    updated = update_note(db, note_id, note_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Note not found")
    return updated

@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a note"""
    deleted = delete_note(db, note_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Note not found")