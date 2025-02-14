from fastapi import Header, HTTPException

API_TOKEN = "static-token-12345"

def authenticate(token: str = Header(...)):
    if token != API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid API token")
