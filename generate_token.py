from jose import jwt

payload = {"sub": "1", "email": "alice@example.com", "username": "alice"}
secret = "your-secret-key-change-in-production-and-match-auth-service"
token = jwt.encode(payload, secret, algorithm="HS256")
print("Token:")
print(token)
