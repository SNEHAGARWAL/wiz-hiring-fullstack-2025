import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load settings from environment variables
load_dotenv()
ASYNC_DATABASE_URL = os.environ.get("DATABASE_URL")

# Create asynchronous engine for SQLAlchemy
db_async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)

# Configure async session factory
AsyncSessionMaker = sessionmaker(
    bind=db_async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for ORM models
DeclarativeBase = declarative_base()

# Dependency to yield a new session for each request
async def acquire_session():
    async with AsyncSessionMaker() as session_instance:
        yield session_instance