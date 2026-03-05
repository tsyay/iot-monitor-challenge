"""
Celery-задача обработки событий от датчиков.

TODO: Реализовать задачу process_sensor_event
- Определить severity по правилам из rules.json
- Если critical — отправить уведомление в Telegram (mock API)
- Сохранить событие в PostgreSQL
- При ошибке Telegram — retry до 3 раз с экспоненциальной задержкой
"""

from app.tasks import celery_app

@celery_app.task
def process_webhook(payload: dict):
    """
    Фоновая обработка вебхука.
    payload — словарь с данными из FastAPI.
    """
    print("Processing webhook in Celery:", payload)
