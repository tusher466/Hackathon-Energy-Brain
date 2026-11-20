from sqlalchemy import Column, Integer, String, DateTime, Float
from app.core.db import Base
from datetime import datetime

class ModelMeta(Base):
    __tablename__ = "model_meta"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    version = Column(String)
    status = Column(String, default="ready")
    trained_at = Column(DateTime, default=datetime.utcnow)
    accuracy = Column(Float, nullable=True)
