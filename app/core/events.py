from app.dependencies.database import create_tables
from app.dependencies.database import async_engine

async def on_startup():
    await create_tables(async_engine)


