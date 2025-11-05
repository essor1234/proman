from fastapi import FastAPI
<<<<<<< HEAD
import uvicorn
from app.core.db import init_db
from app.controllers.user_controller import router as user_router
from app.controllers.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
=======
from core.db import init_db
from controllers.user_controller import router as user_router
from controllers.auth import router as auth_router
>>>>>>> 78c9577d (create a login and microservice that have a function to get user so that my team can get the user info)

# Initialize DB
init_db()

app = FastAPI(title="Account Management Service")
<<<<<<< HEAD

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(auth_router)

=======
app.include_router(user_router)
app.include_router(auth_router)

>>>>>>> 78c9577d (create a login and microservice that have a function to get user so that my team can get the user info)
@app.get("/")
def root():
    return {"message": "User Service is LIVE!"}
