from fastapi import FastAPI
from app.api.routes import upload, process, share, download
from app.core.database import get_db

app = FastAPI()

get_db()

app.include_router(upload.router, prefix="/api")
app.include_router(process.router, prefix="/api")
app.include_router(share.router, prefix="/api")
app.include_router(download.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Welcome to the Video API"}
