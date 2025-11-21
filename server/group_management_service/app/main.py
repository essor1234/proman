from fastapi import FastAPI

# Import all route routers
from app.routes.group_routes import router as group_router
from app.routes.membership_routes import router as membership_router
from app.routes.invitation_routes import router as invitation_router
from app.routes.internal_routes import router as internal_router

# Import database initialization
from app.core.database import init_db

# Create FastAPI app
app = FastAPI(title="Group Management Service")

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()

# Include all routers
app.include_router(group_router)
app.include_router(membership_router)
app.include_router(invitation_router)
app.include_router(internal_router)

# Root endpoint
@app.get("/")
def root():
    return {"message": "Group Management Service is LIVE!"}