from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from config.settings import settings

# Create async engine
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL, echo=settings.DEBUG, future=True
)


async def create_db_and_tables():
    """Create database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


# Import models to ensure they're registered
from .user import User
from .transcript import Transcript

__all__ = ["User", "Transcript", "create_db_and_tables", "engine"]
