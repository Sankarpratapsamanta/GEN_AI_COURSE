from sqlalchemy.ext.asyncio import AsyncSession,async_sessionmaker,create_async_engine

from app.core.config import settings

engine = create_async_engine(settings.database_url)


AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)