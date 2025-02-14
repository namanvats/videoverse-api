from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.services.video_service import share_video
from app.core.database import get_db
from app.core.config import authenticate

router = APIRouter()

@router.post("/share/")
def share_video_api(video_id: str, expiry_minutes: int, db: Session = Depends(get_db), token: str = Depends(authenticate)):
    return share_video(video_id, expiry_minutes, db)
