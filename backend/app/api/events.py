from typing import List, Optional
from fastapi import APIRouter, Query, Depends
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.db import AsyncSessionLocal
from app.models.event import SensorEvent  # SQLAlchemy модель
from pydantic import BaseModel, Field

router = APIRouter()


# Pydantic модель для response
class SensorEventResponse(BaseModel):
    id: str
    sensor_id: str
    location: str
    temperature: float
    humidity: float
    severity: str
    notification_sent: bool
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True  # Для поддержки SQLAlchemy ORM


# Зависимость для сессии
async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


@router.get("/events", response_model=List[SensorEventResponse])
async def get_events(
    sensor_id: Optional[str] = Query(None, description="Фильтр по sensor_id"),
    severity: Optional[str] = Query(None, description="Фильтр по severity"),
    date_from: Optional[datetime] = Query(None, description="Начало диапазона даты"),
    date_to: Optional[datetime] = Query(None, description="Конец диапазона даты"),
    limit: int = Query(50, ge=1, le=1000, description="Количество записей"),
    offset: int = Query(0, ge=0, description="Смещение"),
    session: AsyncSession = Depends(get_session),
):
    # Базовый запрос
    stmt = select(SensorEvent)

    # Фильтры
    filters = []
    if sensor_id:
        filters.append(SensorEvent.sensor_id == sensor_id)
    if severity:
        filters.append(SensorEvent.severity.ilike(f"%{severity}%"))
    if date_from:
        filters.append(SensorEvent.created_at >= date_from)
    if date_to:
        filters.append(SensorEvent.created_at <= date_to)

    if filters:
        stmt = stmt.where(and_(*filters))

    # Сортировка и пагинация
    stmt = stmt.order_by(SensorEvent.created_at.desc()).limit(limit).offset(offset)

    # Выполнение запроса
    result = await session.execute(stmt)
    events = result.scalars().all()

    return events