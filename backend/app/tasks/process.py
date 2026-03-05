import json
import logging
from pathlib import Path
from datetime import datetime
import asyncio
import httpx
import os
from dotenv import load_dotenv

from app.db import AsyncSession, engine
from app.models.event import SensorEvent
from app.tasks import celery_app

# ---------- LOGGING ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger("sensor-processor")

# ---------- ENV ----------
load_dotenv() 

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))
TELEGRAM_API_URL = os.getenv("TELEGRAM_API_URL")
TELEGRAM_SEND_URL = f"{TELEGRAM_API_URL}/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

logger.info(f"Telegram API URL: {TELEGRAM_API_URL}")

# ---------- RULES ----------
RULES_PATH = Path(__file__).resolve().parents[2] / "rules.json"
logger.info(f"Loading rules from {RULES_PATH}")

with open(RULES_PATH) as f:
    RULES = json.load(f)

logger.info(f"Rules loaded: {RULES}")

# ---------- SEVERITY COMPUTATION ----------
def compute_severity(sensor_data: dict) -> dict:
    """Вычисляет уровень severity по правилам RULES"""
    logger.info(f"Computing severity for payload: {sensor_data}")
    severity = {}
    
    for key in ["temperature", "humidity"]:
        value = sensor_data.get(key)
        if value is None:
            continue
        
        thresholds = RULES[key]["thresholds"]
        logger.info(f"Checking {key}: value={value}, warning={thresholds['warning']}, critical={thresholds['critical']}")
        
        if value >= thresholds["critical"]:
            severity[key] = "critical"
        elif value >= thresholds["warning"]:
            severity[key] = "warning"
        else:
            severity[key] = "normal"
    
    logger.info(f"Severity result: {severity}")
    return severity

# ---------- TELEGRAM ----------
async def send_telegram_message(text: str, max_retries: int = 3) -> bool:
    """
    Асинхронная отправка Telegram сообщения с повтором при ошибках.
    """
    logger.info("Preparing to send Telegram message")
    logger.info(f"Message text: {text}, max retries: {max_retries}")

    async with httpx.AsyncClient() as client:
        for attempt in range(max_retries):
            try:
                logger.info(f"Telegram attempt {attempt + 1}")
                response = await client.post(
                    TELEGRAM_SEND_URL,
                    json={"chat_id": TELEGRAM_CHAT_ID, "text": text},
                    timeout=5.0
                )
                logger.info(f"Telegram response status: {response.status_code}")
                response.raise_for_status()
                logger.info("Telegram message sent successfully")
                return True
            except httpx.HTTPError as e:
                wait_time = 2 ** attempt
                logger.warning(f"Telegram attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s")
                await asyncio.sleep(wait_time)

    logger.error("All Telegram attempts failed")
    return False

# ---------- DATABASE ----------
async def save_event(payload: dict, severity: dict, notification_sent: bool):
    """
    Сохраняет событие сенсора в базе данных.
    """
    logger.info("Saving event to database")

    async with AsyncSession(engine) as session:
        try:
            event = SensorEvent(
                sensor_id=payload["sensor_id"],
                location=payload.get("location", ""),
                temperature=payload.get("temperature", 0.0),
                humidity=payload.get("humidity", 0.0),
                severity=", ".join([v for v in severity.values()]),
                notification_sent=notification_sent,
                created_at=datetime.utcnow()
            )
            logger.info(f"Event object created: {event}")
            
            session.add(event)
            await session.commit()
            logger.info(f"Event saved for sensor {payload['sensor_id']}")
        except Exception as e:
            await session.rollback()
            logger.error(f"Database error while saving event: {e}", exc_info=True)
            raise

# ---------- CELERY TASK ----------
@celery_app.task(bind=True)
def process_sensor_event(self, payload: dict):
    """
    Обрабатывает событие сенсора с поддержкой асинхронных операций.
    Используется единый event loop для всех async операций в одной задаче.
    
    При ошибке задача повторяется автоматически (макс. 3 попытки с задержкой 30 сек).
    """
    logger.info("New sensor event received")
    logger.info(f"Payload: {payload}")

    severity = compute_severity(payload)
    logger.info(f"Computed severity: {severity}")

    critical_keys = [k for k, v in severity.items() if v == "critical"]
    notification_sent = False

    try:
        # ✅ КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ: используем ОДИН event loop для всех async операций
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Telegram уведомление (если есть критические значения)
            if critical_keys:
                message = f"CRITICAL ALERT for sensor {payload.get('sensor_id')}: {', '.join(critical_keys)}"
                logger.warning(f"Critical condition detected: {critical_keys}")
                notification_sent = loop.run_until_complete(send_telegram_message(message))
            else:
                logger.info("No critical values detected. Telegram notification skipped.")

            # Сохранение в БД (всегда)
            loop.run_until_complete(save_event(payload, severity, notification_sent))

            logger.info("Sensor event processing finished successfully")

        finally:
            loop.close()

    except Exception as e:
        logger.error(f"Error processing sensor event: {e}", exc_info=True)
        # Автоматический повтор: через 30 секунд, максимум 3 попытки
        raise self.retry(exc=e, countdown=30, max_retries=3)