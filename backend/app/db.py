from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@db:5432/iot_monitor"

# Создаём асинхронный движок
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=True,            # логирование SQL-запросов
    future=True,
)

# Фабрика сессий для async
AsyncSessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

# Базовый класс для моделей
Base = declarative_base()