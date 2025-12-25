from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.gatewayRouter import router as gatewayRouter

app = FastAPI(title="Gateway Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(gatewayRouter)

@app.get("/")
def root():
    return {"message": "Gateway Service is running"}
