from sqlalchemy import Column, String, Integer, BigInteger, Text, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class ThemeTable(Base):
    __tablename__ = 'user_theme'
    theme_name = Column('user_theme', String(30), nullable=False, default=None, primary_key=True)
    telegram_user_id = Column('telegram_user_id', BigInteger, nullable=False, default=None)


class Product(Base):
    __tablename__ = 'products'
    product_id = Column('product_id', String, primary_key=True)
    amount = Column('amount', Float, default=0.0)
    desc = Column('desc', String, default=None)
    activity_day = Column('activity_day', Integer, default=None)


class RandomUserId(Base):
    __tablename__ = 'random_user'
    user_id = Column('telegram_user_id', BigInteger, nullable=False, default=None, primary_key=True)


class Users(Base):
    __tablename__ = "users"
    telegram_user_id = Column('telegram_user_id', BigInteger, nullable=False, default=None, primary_key=True)
    username = Column(String(length=100), nullable=True)
    first_name = Column(String(length=60), nullable=False)
    last_name = Column(String(length=60), nullable=True)
    product_date_end = Column('product_date_end', DateTime, default=None)
    product_id = Column(String, ForeignKey('products.product_id'))
    product = relationship("Product")


class Pay(Base):
    __tablename__ = 'pay'
    user_id = Column('user_id', BigInteger, ForeignKey("users.telegram_user_id"), default=0, primary_key=True)
    payment_id = Column('payment_id', String, default=None)
    intent_id = Column('intent_id', String, default=None)
    user_data = Column('user_data', JSON, default=None)

# date = Column('buy_data', DateTime, default=datetime.utcnow())
