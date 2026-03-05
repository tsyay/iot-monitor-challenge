DATABASE_URL = "postgresql+asyncpg://postgres:postgres@db:5432/iot_monitor"
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# ✅ Параметр pool_pre_ping очень важен для asyncpg
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,        # Проверяет соединение перед использованием
    pool_size=5,               # Ограничить размер пула
    max_overflow=10,           # Макс. доп. соединений
)

AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)