import json
from pathlib import Path
from datetime import datetime
import asyncio
import httpx
import os
from dotenv import load_dotenv

from app.db import AsyncSession, engine
from app.models.event import SensorEvent
from app.tasks import celery_app

load_dotenv() 

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))
TELEGRAM_API_URL = os.getenv("TELEGRAM_API_URL")
TELEGRAM_SEND_URL = f"{TELEGRAM_API_URL}/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

# Путь до rules.json
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

async def send_telegram_message(text: str, max_retries: int = 3):
    """
    Асинхронная отправка в mock Telegram API с экспоненциальной задержкой.
    """
    async with httpx.AsyncClient() as client:
        for attempt in range(max_retries):
            try:
                response = await client.post(
                    TELEGRAM_SEND_URL,
                    json={"chat_id": TELEGRAM_CHAT_ID, "text": text},
                    timeout=5.0
                )
                response.raise_for_status()
                print(f"[Telegram MOCK] Message sent successfully: {text}")
                return True
            except httpx.HTTPError as e:
                wait_time = 2 ** attempt
                print(f"[Telegram MOCK] Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
        print(f"[Telegram MOCK] Failed to send message after {max_retries} attempts")
        return False

async def save_event(payload: dict, severity: dict, notification_sent: bool):
    async with AsyncSession(engine) as session:
        event = SensorEvent(
            sensor_id=payload["sensor_id"],
            location=payload.get("location", ""),
            temperature=payload.get("temperature", 0.0),
            humidity=payload.get("humidity", 0.0),
            severity=", ".join([v for v in severity.values()]),
            notification_sent=notification_sent,
            created_at=datetime.utcnow()
        )
        session.add(event)
        await session.commit()
        print(f"[DB] Event saved for sensor {payload['sensor_id']}")

@celery_app.task
def process_sensor_event(payload: dict):
    """
    Фоновая обработка вебхука с критическим уведомлением.
    """
    print("Received sensor payload:", payload)
    severity = compute_severity(payload)
    print("Calculated severity:", severity)

    critical_keys = [k for k, v in severity.items() if v == "critical"]
    notification_sent = False

    if critical_keys:
        message = f"CRITICAL ALERT for sensor {payload.get('sensor_id')}: {', '.join(critical_keys)}"
        print("[Telegram MOCK]", message)
        notification_sent = asyncio.run(send_telegram_message(message))

    asyncio.run(save_event(payload, severity, notification_sent))