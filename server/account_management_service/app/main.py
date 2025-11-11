from fastapi import FastAPI
from core.db import init_db
from controllers.user_controller import router as user_router
from controllers.auth import router as auth_router

# Initialize DB
init_db()

app = FastAPI(title="Account Management Service")
app.include_router(user_router)
app.include_router(auth_router)

@app.get("/")
def root():
    return {"message": "User Service is LIVE!"}
