from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import asynccontextmanager

DATABASE_URL = "postgresql+asyncpg://postgres:akrSQL%4005@localhost:5432/debate_arena"

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

@asynccontextmanager
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
