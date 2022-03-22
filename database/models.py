from sqlalchemy import Column, String, Integer, BigInteger, Text, DateTime
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

# class AnonimUser(Base):
#     __tablename__ = "anonim_user"


class UserProfile(Base):
    __tablename__ = "user_profile"
    id = Column('id', Integer, primary_key=True)
    telegram_user_id = Column('telegram_user_id', BigInteger, nullable=False, default=None)
    login = Column('login', String(20))
    sub = Column('date_sub', DateTime(timezone=True), default=None, nullable=True)
