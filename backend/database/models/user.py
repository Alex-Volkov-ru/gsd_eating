from sqlalchemy import Column, Integer, BigInteger, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from database.create import Base


class User(Base):
    """Модель пользователя бота"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    tg_id = Column(BigInteger, unique=True, index=True)
    username = Column(String, nullable=True)
    register_date = Column(DateTime, server_default=func.now())

    meals = relationship("Meal", back_populates="user")
    blood_records = relationship("BloodRecord",
                                 back_populates="user",
                                 cascade="all, delete-orphan")
