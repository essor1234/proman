"""
Utility functions for SQLAlchemy ORM models, specifically reusable column definitions.
"""
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from uuid import uuid4


def UUIDColumn(primary_key=False, index=False, nullable=False, default=None):
    """
    Helper function to define a UUID column using String(36) for broad database compatibility.
    Defaults to generating a new UUID string for primary keys if not provided.
    """
    # Using String(36) to store UUID strings for broad database compatibility
    return Column(
        String(36), 
        primary_key=primary_key, 
        index=index, 
        nullable=nullable, 
        default=lambda: str(uuid4()) if default is None else default
    )       