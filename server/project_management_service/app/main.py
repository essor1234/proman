# In main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from db.database import engine, Base

# Import the router objects from your route files
from routes import user, group, project

# This line tells SQLAlchemy to create all tables defined in your models
# that inherit from Base if they don't already exist.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Project management service",
    description="Manage your own project",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    # allow_origins=settings.ALLOW_ORIGINS, # Uncomment and configure as needed
    allow_origins=["*"], # Example: Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the routers from the other files
app.include_router(user.router)
app.include_router(group.router)
app.include_router(project.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Project Management API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)