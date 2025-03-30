from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship

from database.create import Base


class Meal(Base):
    """Модель записи о приёме пищи"""
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    meal_type_id = Column(Integer, ForeignKey('meal_types.id'))

    description = Column(Text)
    meal_time = Column(DateTime, index=True)

    # Используйте строки для ленивой загрузки отношений
    user = relationship("User", back_populates="meals")
    meal_type = relationship("MealType", lazy="joined")
