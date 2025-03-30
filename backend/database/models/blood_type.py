from sqlalchemy import Column, Integer, String

from database.create import Base


class BloodType(Base):
    """Модель типов приёмов крови"""
    __tablename__ = "blood_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return f"<BloodType {self.id}: {self.name}>"
