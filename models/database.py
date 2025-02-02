from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    videos = relationship("Video", back_populates="user")

class Video(Base):
    __tablename__ = 'videos'
    
    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    upload_time = Column(DateTime, default=datetime.utcnow)
    processing_time = Column(Float)  # in seconds
    frame_count = Column(Integer)
    extracted_count = Column(Integer)
    status = Column(String)  # 'processing', 'completed', 'failed'
    
    user = relationship("User", back_populates="videos")
    extracted_images = relationship("ExtractedImage", back_populates="video")

class ExtractedImage(Base):
    __tablename__ = 'extracted_images'
    
    id = Column(Integer, primary_key=True)
    video_id = Column(Integer, ForeignKey('videos.id'))
    filename = Column(String, nullable=False)
    frame_number = Column(Integer)
    confidence_score = Column(Float)
    timestamp = Column(Float)  # timestamp in video
    extraction_time = Column(DateTime, default=datetime.utcnow)
    
    video = relationship("Video", back_populates="extracted_images")

def init_db(db_url='postgresql://localhost/video_extractor'):
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()
