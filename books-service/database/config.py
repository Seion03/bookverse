import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from typing import AsyncGenerator
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("BOOKS_DB_URL", "postgresql+asyncpg://user:pass@localhost:5434/booksdb")

engine = create_async_engine (
    DATABASE_URL,
    echo=True, #logs for all sql queries for debussing
    pool_size=20, #maintaing 20 persistent connections in the pool
    max_overflow=0, #preventing over connections from the pool size
    pool_pre_ping=True, #check if the connections are still up
    pool_recycle=300, #Recycle and refresh connections every 300 seconds
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    '''
    Dependancy to get a database session
    '''
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()