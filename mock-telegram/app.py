from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import random

app = FastAPI(title="Mock Telegram Bot API")

messages_db = {}

class SendMessageRequest(BaseModel):
    chat_id: int
    text: str


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/bot{token}/sendMessage")
async def send_message(token: str, body: SendMessageRequest):

    # 10% вероятность ошибки
    if random.random() < 0.1:
        raise HTTPException(status_code=500, detail="Simulated Telegram failure")

    if token not in messages_db:
        messages_db[token] = []

    message = {
        "chat_id": body.chat_id,
        "text": body.text
    }

    messages_db[token].append(message)

    return {
        "ok": True,
        "result": message
    }


@app.get("/bot{token}/messages")
async def get_messages(token: str) -> List[dict]: 
    return messages_db.get(token, [])


for route in app.routes:
    print(route.path) 