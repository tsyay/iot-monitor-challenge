"""
Webhook endpoint для приёма данных от IoT-датчиков.

TODO: Реализовать обработчик POST /webhooks/sensor
- Принять JSON с полями: sensor_id, location, temperature, humidity, timestamp
- Валидировать данные через Pydantic
- Отправить задачу в Celery-очередь
- Вернуть {"status": "accepted", "task_id": "..."}
"""

from datetime import datetime
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.tasks.process import process_webhook

router = APIRouter()

class SensorPayload(BaseModel):
    sensor_id: str
    location: str
    temperature: float
    humidity: float
    timestamp: datetime

@router.post("/sensor")
async def webhook_endpoint(payload: SensorPayload):
    try:
        print("Received sensor payload:", payload)
        task = process_webhook.delay(payload.dict())        
        return JSONResponse(content={"status": "accepted", "task_id": task.id})
    except Exception as e:
        return JSONResponse(content={"status": "error", "detail": str(e)}, status_code=400)