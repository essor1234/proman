# app/controllers/base_controller.py
import uuid
from ..core.database import use_uuid

def to_db_id(val):
    """
    Convert input to database-compatible ID.
    - If using PostgreSQL (native UUIDs): convert to uuid.UUID
    - If using SQLite (string UUIDs): leave as string
    """
    if val is None:
        return None

    if use_uuid:
        try:
            return uuid.UUID(str(val))
        except Exception:
            raise ValueError(f"Invalid UUID: {val}")
    else:
        # For SQLite, just return string
        return str(val)
