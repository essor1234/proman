# gen_token.py
from jose import jwt
from datetime import datetime, timedelta

# --- UPDATE THIS LINE ---
# Paste the EXACT key from app/core/config.py here
SECRET_KEY = "sdafefdfdsfa2312324"
print(f"Script Key First 5 chars: {SECRET_KEY[:5]}")
# ------------------------

ALGORITHM = "HS256"

def create_test_token(user_id: int):
    expire = datetime.utcnow() + timedelta(days=1)
    to_encode = {
        "sub": str(user_id), # Validates against get_current_user
        "exp": expire
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print("\n--- YOUR TEST TOKEN ---")
    print(f"Bearer {encoded_jwt}")
    print("-----------------------\n")

# NOTE: Ensure User ID 1 exists in your database logic if you are testing DB constraints
create_test_token(user_id=1)