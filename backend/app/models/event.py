"""
SQLAlchemy модель для хранения событий датчиков.

TODO: Реализовать модель SensorEvent
- id (PK)
- sensor_id (str)
- location (str)
- temperature (float)
- humidity (float)
- severity (str): normal / warning / critical
- notification_sent (bool)
- error_message (str, nullable)
- created_at (datetime)
"""

from sqlalchemy import Column, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class SensorEvent(Base):
    __tablename__ = "sensor_events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    sensor_id = Column(String, nullable=False)
    location = Column(String, nullable=False)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    severity = Column(String, nullable=False)  # normal / warning / critical
    notification_sent = Column(Boolean, default=False, nullable=False)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


