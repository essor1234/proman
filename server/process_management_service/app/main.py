from fastapi import FastAPI

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.todo_function.core.database import engine

from app.todo_function.routes.moscow import router as moscow_router
from app.todo_function.routes.task import router as task_router
from app.todo_function.routes.todo import router as todo_router

from app.todo_function.core.database import engine, Base 
import uvicorn



app = FastAPI()

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

# 2. Include the Router
app.include_router(moscow_router)
app.include_router(task_router)
app.include_router(todo_router)

@app.get("/")
def root():
    return {"message": "Process Management Service is running"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)