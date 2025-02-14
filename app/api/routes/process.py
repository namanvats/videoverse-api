from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.services.video_service import trim_video, merge_videos
from app.core.database import get_db
from typing import List
from app.core.config import authenticate
from pydantic import BaseModel

router = APIRouter()

class MergeRequest(BaseModel):
    video_ids: List[str]

@router.post("/trim/")
def trim_video_api(video_id: str, start_time: str, end_time: str, db: Session = Depends(get_db), token: str = Depends(authenticate)):
    return trim_video(video_id, start_time, end_time, db)

@router.post("/merge/")
def merge_videos_api(request: MergeRequest, db: Session = Depends(get_db), token: str = Depends(authenticate)):
    return merge_videos(request.video_ids, db)