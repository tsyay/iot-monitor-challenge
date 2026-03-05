# backend/app/tasks/process.py
import json
from pathlib import Path
from datetime import datetime
import asyncio

from app.db import AsyncSession, engine
from app.models.event import SensorEvent  # импорт из файла event.py
from app.tasks import celery_app

# Путь до rules.json относительно backend/
RULES_PATH = Path(__file__).resolve().parents[2] / "rules.json"
with open(RULES_PATH) as f:
    RULES = json.load(f)

def compute_severity(sensor_data: dict) -> dict:
    severity = {}
    for key in ["temperature", "humidity"]:
        value = sensor_data.get(key)
        if value is None:
            continue
        thresholds = RULES[key]["thresholds"]
        if value >= thresholds["critical"]:
            severity[key] = "critical"
        elif value >= thresholds["warning"]:
            severity[key] = "warning" 
        else:
            severity[key] = "normal"
    return severity

@celery_app.task
def process_sensor_event(payload: dict):
    """
    Фоновая обработка вебхука.
    """
    print("Received sensor payload:", payload)
    severity = compute_severity(payload)
    print("Calculated severity:", severity)

    critical_keys = [k for k, v in severity.items() if v == "critical"]
    if critical_keys:
        message = f"CRITICAL ALERT for sensor {payload.get('sensor_id')}: {', '.join(critical_keys)}"
        print("[Telegram MOCK]", message)

    asyncio.run(save_event(payload, severity))

async def save_event(payload: dict, severity: dict):
    async with AsyncSession(engine) as session:
        event = SensorEvent(
            sensor_id=payload["sensor_id"],
            location=payload.get("location", ""),
            temperature=payload.get("temperature", 0.0),
            humidity=payload.get("humidity", 0.0),
            severity=", ".join([v for v in severity.values()]),  # сохраняем все уровни
            notification_sent=any(v == "critical" for v in severity.values()),
            created_at=datetime.utcnow()
        )
        session.add(event)
        await session.commit()