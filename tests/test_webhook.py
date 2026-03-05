import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock

# Абсолютные импорты в проекте
from backend.app.main import app
from backend.app.tasks import process_sensor_event

@pytest.mark.asyncio
async def test_webhook_valid_data():
    # -------------------
    # валидный payload для webhook
    # -------------------
    valid_payload = {
        "sensor_id": 1,
        "temperature": 25,
        "humidity": 40,
        "location": "Room 101"
    }

    # -------------------
    # Мокаем Celery задачу
    # -------------------
    mock_task = MagicMock()
    mock_task.id = "fake-task-id"

    # -------------------
    # Мокаем RULES, чтобы json не грузился
    # -------------------
    mock_rules = {
        "temperature": {"thresholds": {"warning": 50, "critical": 70}},
        "humidity": {"thresholds": {"warning": 70, "critical": 90}}
    }

    with patch.object(process_sensor_event, "delay", return_value=mock_task), \
         patch("backend.app.tasks.process.RULES", mock_rules):
        
        # -------------------
        # Отправляем POST запрос к webhook
        # -------------------
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/webhook", json=valid_payload)

    # -------------------
    # Проверяем ответ
    # -------------------
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["task_id"] == "fake-task-id"