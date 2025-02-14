from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.services.video_service import trim_video, merge_videos
from app.core.database import get_db
from app.core.config import authenticate

router = APIRouter()

@router.post("/trim/")
def trim_video_api(video_id: str, start_time: str, end_time: str, db: Session = Depends(get_db), token: str = Depends(authenticate)):
    return trim_video(video_id, start_time, end_time, db)

@router.post("/merge/")
def merge_videos_api(video_ids: list, db: Session = Depends(get_db), token: str = Depends(authenticate)):
    return merge_videos(video_ids, db)
