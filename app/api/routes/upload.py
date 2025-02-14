from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.services.video_service import save_video
from app.core.database import get_db
from app.core.config import authenticate

router = APIRouter()

@router.post("/upload/")
def upload_video(file: UploadFile = File(...), max_size_mb: int = 25, db: Session = Depends(get_db), token: str = Depends(authenticate)):
    video = save_video(file, max_size_mb, db)
    return {"message": "File uploaded successfully", "file_id": video.id}
