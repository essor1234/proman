import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from core.db import init_db
from controllers.auth import router

# CALL init_db() FIRST — BEFORE ANYTHING
init_db()  # ← THIS CREATES TABLES

app = FastAPI()
app.include_router(router)

@app.on_event("startup")
def start():
    print("App started! Tables are ready.")