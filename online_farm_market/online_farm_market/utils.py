import json
import os
from passlib.hash import pbkdf2_sha256

SESSION_FILE = os.path.join(os.path.dirname(__file__), ".session.json")

def hash_password(password: str) -> str:
    return pbkdf2_sha256.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pbkdf2_sha256.verify(password, hashed)

def save_session(data: dict):
    with open(SESSION_FILE, "w") as f:
        json.dump(data, f)

def load_session():
    if not os.path.exists(SESSION_FILE):
        return None
    try:
        with open(SESSION_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return None

def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
