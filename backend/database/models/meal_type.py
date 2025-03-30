from sqlalchemy import Column, Integer, String

from database.create import Base


class MealType(Base):
    """Модель типов приёмов пищи"""
    __tablename__ = "meal_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return f"<MealType {self.id}: {self.name}>"
