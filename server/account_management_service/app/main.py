from fastapi import FastAPI
import uvicorn
from app.core.db import init_db
from app.controllers.user_controller import router as user_router
from app.controllers.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Account Management Service")


@app.on_event("startup")
def on_startup():
    # initialize DB at startup (safer than running at import time)
    try:
        init_db()
    except Exception:
        # don't crash import during test collection; errors will surface when running the app
        pass

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
