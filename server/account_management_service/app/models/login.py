# Create a new file, for example: models/auth.py
from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str