from sqlalchemy import Column, String, Integer, BigInteger, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import column_property
from .base import Base


class ThemeTable(Base):
    __tablename__ = 'user_theme'
    id = Column('id', Integer, primary_key=True)
    theme_name = Column('user_theme', String(30), nullable=False, default=None)
    telegram_user_id = Column('telegram_user_id', BigInteger, nullable=False, default=None)


class RandomUserId(Base):
    __tablename__ = 'random_user'
    id = Column('id', Integer, primary_key=True)
    user_id = Column('telegram_user_id', BigInteger, nullable=False, default=None)


class Users(Base):
    __tablename__ = "users"
    id = Column('id', Integer, primary_key=True)
    telegram_user_id = Column('telegram_user_id', BigInteger, nullable=False, default=None)
    first_name = Column(String(length=60), nullable=False)
    last_name = Column(String(length=60), nullable=True)
    username = Column(String(length=100), nullable=True)
    sub = Column('date_sub', DateTime(timezone=True), default=None, nullable=True)
    start_data = Column('start_date', DateTime(timezone=True), default=None, nullable=True)

