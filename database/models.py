from sqlalchemy import Column, String, Table, Integer, BigInteger, Text, DateTime, Float, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


# user_report = Table('user_report', Base.metadata,
#                     Column("user_id", ForeignKey("users.telegram_user_id"), primary_key=True),
#                     Column("report_id", ForeignKey("report.id"), primary_key=True)
#                     )


class Product(Base):
    __tablename__ = 'products'
    product_id = Column('product_id', String, primary_key=True)
    amount = Column('amount', Float, default=0.0)
    desc = Column('desc', String, default=None)
    activity_day = Column('activity_day', Integer, default=None)



class Users(Base):
    __tablename__ = "users"
    telegram_user_id = Column('telegram_user_id', BigInteger, nullable=False, default=None, primary_key=True)
    username = Column(String(length=100), nullable=True)
    first_name = Column(String(length=60), nullable=False)
    last_name = Column(String(length=60), nullable=True)
    timeout = Column('timeout', DateTime, default=None)
    product_date_end = Column('product_date_end', DateTime, default=None)
    top_date_end = Column("top_date_end", DateTime, default=None)
    complaints = relationship("Report", lazy="joined", cascade="all, delete-orphan")
    success_payment = relationship("SuccessPay", lazy="joined", cascade="all, delete-orphan")
    ban = Column('ban', Boolean, default=False)
    sub_ban = Column('sub_ban', Boolean, default=False)
    time_ban = Column('time_ban', DateTime, default=None)
    is_human = Column('is_human', Boolean, default=False)
    top = Column('top', Boolean, default=False)
    attempts = Column('attempts', Integer, default=6)
    ban_info = Column('ban_info', String, default=None)
    gender = Column('gender', String, default=None)


class Report(Base):
    __tablename__ = 'report'
    id = Column(Integer, primary_key=True)
    complaint = Column('complaint', String, default=None)
    counter = Column('counter', Integer, default=0)
    user_id = Column("user_id", BigInteger, ForeignKey("users.telegram_user_id"))


class Pay(Base):
    __tablename__ = 'pay'
    payment_id = Column('payment_id', BigInteger, default=None, primary_key=True)
    user_id = Column('user_id', BigInteger, default=None)
    intent_id = Column('intent_id', String, default=None)
    product_data = Column('product_data', JSON, default=None)
    user_data = Column('user_data', JSON, default=None)
    date = Column('buy_data', DateTime, default=datetime.utcnow())


class SuccessPay(Base):
    __tablename__ = 'success_pay'
    payment_id = Column('payment_id', BigInteger, default=None, primary_key=True)
    user_id = Column('user_id', BigInteger, ForeignKey("users.telegram_user_id"))
    product_id = Column('product_id', String, ForeignKey("products.product_id"))
    date = Column('buy_data', DateTime, default=datetime.utcnow())
