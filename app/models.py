from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, text, Date, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, date

from .database import Base


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(50), unique=True)
    phone_number = Column(String(50), unique=True)
    role = Column(String)

    attendance_table = relationship("Attendance", back_populates="user_table")


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String)
    email = Column(String, ForeignKey("users.email", ondelete="CASCADE"))
    present = Column(Boolean, default=True)
    signed_in = Column(DateTime, default=datetime.now())
    session = Column(String, nullable=False)
    created_at = Column(Date, default=date.today())

    user_table = relationship(Users, back_populates="attendance_table")