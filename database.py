import os
from dotenv import load_dotenv
import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, DateTime, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from datetime import datetime
from config import DATABASE_URL

engine = create_async_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} # для sqlite
)

async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer, 
        primary_key= True,
        index= True
        )
    username = Column(
        String,
        unique= True,
        index= True
    )
    hashed_password = Column(String)
    email = Column(
        String,
        unique= True,
        nullable= True
    )
    created_at = Column(
        DateTime,
        default= datetime.utcnow
    )

class Link(Base):
    __tablename__ = "links"

    id = Column(
        Integer,
        primary_key= True,
        index= True
    )
    short_code = Column(
        String,
        unique= True,
        index= True
    )
    original_url = Column(String)
    created_at = Column(
        DateTime,
        default= datetime.utcnow
    )
    expires_at = Column(
        DateTime,
        nullable= True
    )
    user_id = Column(
        Integer,
        sqlalchemy.ForeignKey("users.id"),
        nullable= True
    )

class LinkStats(Base):
    __tablename__ = "link_stats"

    id = Column(
        Integer,
        primary_key= True,
        index= True
    )
    link_id = Column(
        Integer,
        sqlalchemy.ForeignKey("links.id")
    )
    created_at = Column(
        DateTime,
        default= datetime.utcnow
    )
    user_agent = Column(
        String,
        nullable= True
    )
    ip_address = Column(
        String,
        nullable= True
    )

class Counter(Base):
    __tablename__ = "counter"

    id = Column(
        Integer,
        primary_key= True
        )
    next_value = Column(
        BigInteger,
        default=1
    )


async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)