from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

async_engine = create_async_engine(settings.DATABASE_URL, echo=True)
AsyncSessionFactory = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    autoflush=False,
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionFactory() as session:
        yield session

async def create_tables(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
