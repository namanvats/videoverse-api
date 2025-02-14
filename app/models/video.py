from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
import uuid
import datetime

Base = declarative_base()

class Video(Base):
    __tablename__ = "videos"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, index=True)
    filepath = Column(String)
    upload_time = Column(DateTime, default=datetime.datetime.utcnow)
    expiry_time = Column(DateTime, nullable=True)
