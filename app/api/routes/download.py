from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.video import Video
import datetime

router = APIRouter()

@router.get("/download/{video_id}")
def download_video(video_id: str, db: Session = Depends(get_db)):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video or (video.expiry_time and video.expiry_time < datetime.datetime.utcnow()):
        raise HTTPException(status_code=404, detail="Video not found or expired")
    
    return FileResponse(path=video.filepath, filename=video.filename, media_type="video/mp4")
