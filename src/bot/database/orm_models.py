from datetime import datetime, timezone

from sqlalchemy import BigInteger, Column, DateTime, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True)
    grade = Column(String, nullable=True)


class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger)
    text = Column(String)
    status = Column(String, default="pending")
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
