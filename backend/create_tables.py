import asyncio
from app.database import db_async_engine
from app import models

async def run_migrations():
    # Asynchronously create all tables defined in models
    async with db_async_engine.begin() as connection:
        await connection.run_sync(models.DeclarativeBase.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(run_migrations())