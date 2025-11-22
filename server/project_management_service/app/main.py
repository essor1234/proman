"""
Main application file for the Project Management Service.
Handles application setup, CORS middleware, database initialization, and router inclusion.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
# Ensure Base and engine are imported from your core database setup
from app.core.database import engine, Base 
# Import the router objects from your route files
from app.routes import group, project


# Application Initialization
app = FastAPI(
    title="Project management service",
    description="Manage your own project",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Database Table Creation on Startup
@app.on_event("startup")
def on_startup():
    """
    Called when the application starts. Ensures all necessary database tables 
    (Groups, Projects, Junction tables) are created if they don't exist.
    """
    # This line tells SQLAlchemy to create all tables defined in your models
    # that inherit from Base if they don't already exist.
    Base.metadata.create_all(bind=engine)
    print("Database tables ensured to exist on startup.")


# CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allowing all origins for development/testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root Endpoint (Only one definition kept)
@app.get("/", tags=["Root"])
def read_root():
    """Welcome message and root endpoint access."""
    return {"message": "Welcome to the Project Management API"}


# Include the routers from the other files
app.include_router(group.router, prefix="/groups")
app.include_router(project.router, prefix="/projects")


# Uvicorn entry point (optional if running via CLI, but useful for local testing)
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)