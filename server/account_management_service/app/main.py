from fastapi import FastAPI
import uvicorn
from app.core.db import init_db
from app.controllers.user_controller import router as user_router
from app.controllers.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware

# Initialize DB
init_db()

app = FastAPI(title="Account Management Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(auth_router)

@app.get("/")
def root():
    return {"message": "User Service is LIVE!"}
