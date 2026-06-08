"""
ORM-модели хранилища данных.
Структура: Timestamp / Режим / Аномалия по датчику
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from server.storage.database import Base


class SensorRecord(Base):
    __tablename__ = "sensor_records"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    sensor_name = Column(String(16), nullable=False, index=True)
    value = Column(Float, nullable=False)
    mode = Column(String(32), nullable=False)
    anomaly = Column(Boolean, default=False)
    anomaly_description = Column(String(256), nullable=True)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    hashed_password = Column(String(256), nullable=False)
    role = Column(String(32), default="operator")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
