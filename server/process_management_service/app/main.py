from fastapi import FastAPI

# Create a FastAPI app instance
# This is the main application file for the Process Management Service.
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Process Management Service is running"}
