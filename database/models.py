from sqlalchemy import Column, String, Integer, BigInteger
from .base import Base


class ThemeTable(Base):
    __tablename__ = 'user_theme'
    id = Column('id', Integer, primary_key=True)
    theme_name = Column('user_theme', String(30), nullable=False, default=None)
    telegram_user_id = Column('telegram_user_id', BigInteger, nullable=False, default=None)


class RandomUserId(Base):
    __tablename__ = 'random_user'
    id = Column('id', Integer, primary_key=True)
    user_id = Column('user_id', BigInteger, nullable=False, default=None)
