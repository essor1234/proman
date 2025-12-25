from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.core.database import engine, Base 
from app.routes import project 
# Removed: from app.routes import group

app = FastAPI(
    title="Project management service",
    description="Manage your own project",
    version="0.1.0",
)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    print("Database tables ensured to exist on startup.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Removed: app.include_router(group.router, prefix="/groups")
app.include_router(project.router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)