import os

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

url = f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine: AsyncEngine = create_async_engine(
    url,
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,
    pool_pre_ping=True,
    pool_timeout=5,
)

sessionmaker = async_sessionmaker(bind=engine, expire_on_commit=False)
