from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.core.config import DATABASE_URL


# async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_recycle=3600
)
# session maker object for opening session to connect to DB
new_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
    autoflush=True,
    autocommit=False
)


# Declarative base for creating table modules, like Interface
class Base(DeclarativeBase):
    pass


# Function for getting session
async def get_session() -> AsyncSession:
    async with new_session() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise
        finally:
            await session.close()


