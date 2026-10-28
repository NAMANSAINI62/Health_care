import os
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from config import settings

logger = logging.getLogger("database")

database_url = settings.DATABASE_URL
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

Base = declarative_base()

def get_engine(url: str):
    return create_async_engine(
        url,
        echo=False,
        future=True,
        connect_args={"statement_cache_size": 0}
    )

engine = get_engine(database_url)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db_tables():
    """Initializes tables on PostgreSQL database."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("PostgreSQL database connected and tables initialized.")
    except Exception as e:
        logger.warning(f"Could not connect to database on startup ({e}). Will retry on incoming requests.")

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
