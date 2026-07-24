import os
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from config import settings

logger = logging.getLogger("database")

database_url = settings.DATABASE_URL
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# Default to SQLite if postgres URL has default placeholder or environment variable is missing
use_sqlite = False

Base = declarative_base()

def get_engine(url: str):
    return create_async_engine(url, echo=False, future=True)

# Primary Engine
try:
    engine = get_engine(database_url)
except Exception:
    database_url = "sqlite+aiosqlite:///./aivoa_complaints.db"
    engine = get_engine(database_url)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db_tables():
    """Initializes tables. If PostgreSQL connection fails (e.g. invalid auth), fallback to local SQLite."""
    global engine, AsyncSessionLocal, database_url
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Primary database connected and tables initialized.")
    except Exception as e:
        logger.warning(f"PostgreSQL connection failed ({e}). Switching to local SQLite database...")
        database_url = "sqlite+aiosqlite:///./aivoa_complaints.db"
        engine = get_engine(database_url)
        AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Local SQLite database initialized.")

async def get_db():
    global engine, AsyncSessionLocal
    try:
        async with AsyncSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()
    except Exception:
        # Emergency session fallback to SQLite if PostgreSQL fails mid-session
        fallback_url = "sqlite+aiosqlite:///./aivoa_complaints.db"
        engine = get_engine(fallback_url)
        AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        async with AsyncSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()
