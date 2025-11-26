from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite database URL
SQLALCHEMY_DATABASE_URL = "sqlite:////data/group_service.db"

# Create SQLAlchemy engine
# check_same_thread=False is needed only for SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=True  # Set to False in production to disable SQL query logging
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session.
    Use this in FastAPI route dependencies.
    
    Example:
        @router.get("/groups")
        def get_groups(db: Session = Depends(get_db)):
            # Use db here
            pass
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    Creates all tables defined in models.
    Call this on application startup.
    
    Example in main.py:
        @app.on_event("startup")
        def startup_event():
            init_db()
    """
    # Import all models here to ensure they are registered with Base
    from ..models.group import Group
    from ..models.membership import Membership
    
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")


def drop_all_tables():
    """
    Drop all tables from database.
    WARNING: This will delete all data!
    Use only for development/testing.
    """
    Base.metadata.drop_all(bind=engine)
    print("⚠️ All tables dropped!")


def reset_db():
    """
    Reset database by dropping and recreating all tables.
    WARNING: This will delete all data!
    Use only for development/testing.
    """
    drop_all_tables()
    init_db()
    print("🔄 Database reset complete!")