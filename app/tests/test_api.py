import os
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app, get_db
from app.models.video import Base, Video

# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_video_api.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create tables for testing
Base.metadata.create_all(bind=engine)

# Initialize test client
client = TestClient(app)

# Static test token
TEST_TOKEN = "static-token-12345"

@pytest.fixture(scope="function")
def cleanup():
    """Cleanup database before each test"""
    db = TestingSessionLocal()
    db.query(Video).delete()
    db.commit()
    db.close()
    yield

def test_upload_video(cleanup):
    """Test uploading a video file"""
    test_file = ("test.mp4", b"fake video content")
    response = client.post(
        "/api/upload/",
        headers={"token": TEST_TOKEN},
        files={"file": test_file}
    )
    assert response.status_code == 200
    assert "file_id" in response.json()

def test_download_video(cleanup):
    """Test downloading a video file"""
    # Upload a test video
    test_file = ("test.mp4", b"fake video content")
    upload_response = client.post("/api/upload/", headers={"token": TEST_TOKEN}, files={"file": test_file})

    assert upload_response.status_code == 200
    video_id = upload_response.json()["file_id"]

    # Download the video
    response = client.get(f"/api/download/{video_id}", headers={"token": TEST_TOKEN})
    assert response.status_code == 200
    assert response.headers["content-type"] == "video/mp4"

def test_invalid_auth():
    """Test request with invalid authentication"""
    response = client.post("/api/upload/", headers={"token": "invalid-token"}, files={"file": ("test.mp4", b"fake")})
    assert response.status_code == 401

def test_invalid_merge_request(cleanup):
    """Test merging with non-existent videos"""
    response = client.post(
        "/merge/",
        headers={"token": TEST_TOKEN, "Content-Type": "application/json"},
        json={"video_ids": ["invalid-id1", "invalid-id2"]}
    )
    assert response.status_code == 404
