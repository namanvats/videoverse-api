import os
import uuid
import datetime
import re
import subprocess
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.video import Video

UPLOAD_DIR = "./uploads"
MERGED_DIR = "./merged"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(MERGED_DIR, exist_ok=True)

def save_video(file, max_size_mb, db: Session):
    file_size = file.file.read()
    file.file.seek(0)
    if len(file_size) > max_size_mb * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File size exceeds {max_size_mb}MB limit")

    filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = f"{UPLOAD_DIR}/{filename}"

    with open(file_path, "wb") as buffer:
        buffer.write(file_size)

    video = Video(filename=file.filename, filepath=file_path)
    db.add(video)
    db.commit()
    db.refresh(video)
    return video

def trim_video(video_id: str, start_time: str, end_time: str, db: Session):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    time_format = re.compile(r"^(\d{2}):(\d{2}):(\d{2})$")
    if not time_format.match(start_time) or not time_format.match(end_time):
        raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM:SS")

    trimmed_filename = f"trimmed_{video.filename}"
    trimmed_filepath = os.path.join("./uploads", trimmed_filename)

    command = [
        "ffmpeg", "-i", video.filepath,
        "-ss", start_time, "-to", end_time, "-c", "copy", trimmed_filepath
    ]

    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if process.returncode != 0:
        raise HTTPException(status_code=500, detail=f"Error trimming video: {process.stderr.decode()}")

    # Store trimmed video path in DB
    video.filepath = trimmed_filepath
    db.commit()

    return {"message": "Video trimmed successfully", "video_id": video.id, "trimmed_file": trimmed_filepath}


def merge_videos(video_ids: list, db: Session):
    videos = db.query(Video).filter(Video.id.in_(video_ids)).all()
    if len(videos) != len(video_ids):
        raise HTTPException(status_code=404, detail="One or more videos not found")
    
    input_txt_path = os.path.join(MERGED_DIR, "input.txt")
    merged_filename = f"merged_{uuid.uuid4()}.mp4"
    merged_filepath = os.path.join(MERGED_DIR, merged_filename)

    preprocessed_files = []
    for video in videos:
        preprocessed_file = os.path.join(MERGED_DIR, f"preprocessed_{uuid.uuid4()}.mp4")

        preprocess_command = [
            "ffmpeg", "-i", video.filepath, "-vf", "setpts=PTS-STARTPTS", "-af", "asetpts=PTS-STARTPTS",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-c:a", "aac", "-b:a", "192k", "-y", preprocessed_file
        ]
        process = subprocess.run(preprocess_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if process.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Error preprocessing video: {process.stderr.decode()}")

        if not os.path.exists(preprocessed_file):
            raise HTTPException(status_code=500, detail=f"Preprocessed file not found: {preprocessed_file}")

        preprocessed_files.append(preprocessed_file)

    with open(input_txt_path, "w") as f:
        for preprocessed in preprocessed_files:
            f.write(f"file '{os.path.abspath(preprocessed)}'\n")

    command = ["ffmpeg", "-f", "concat", "-safe", "0", "-i", input_txt_path, "-c", "copy", merged_filepath]
    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if process.returncode != 0:
        raise HTTPException(status_code=500, detail=f"Error merging videos: {process.stderr.decode()}")

    merged_video = Video(filename=merged_filename, filepath=merged_filepath)
    db.add(merged_video)
    db.commit()
    db.refresh(merged_video)

    return {"message": "Videos merged successfully", "merged_video_id": merged_video.id, "download_url": f"/api/download/{merged_video.id}"}


def share_video(video_id: str, expiry_minutes: int, db: Session):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    expiry_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=expiry_minutes)
    video.expiry_time = expiry_time
    db.commit()

    return {
        "message": "Video link shared successfully",
        "expiry_time": expiry_time,
        "download_url": f"/api/download/{video_id}"
    }
