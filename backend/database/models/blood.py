from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database.create import Base


class BloodRecord(Base):
    """Модель записи показателя сахара в крови"""
    __tablename__ = "blood_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    date_time = Column(DateTime, index=True)
    glucose = Column(Float)
    blood_type_id = Column(Integer, ForeignKey('blood_types.id'))

    user = relationship("User", back_populates="blood_records")
    blood_type = relationship("BloodType", lazy='joined')

    def __repr__(self):
        return f"<BloodRecord {self.date_time}: {self.glucose} mmol/L>"
