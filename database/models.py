from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Integer, BigInteger
from loader import engine, session

Base = declarative_base(bind=engine)


class ThemeTable(Base):
    __tablename__ = 'user_theme'
    id = Column('id', Integer, primary_key=True)
    theme_name = Column('user_theme', String(50), nullable=False, default=None)
    telegram_user_id = Column('telegram_user_id', BigInteger, nullable=False, default=None)

    def __repr__(self):
        return {f"Пользователя с id {self.telegram_user_id} задал данную тему {self.theme_name}"}

    @classmethod
    def get_all_theme(cls):
        return session.query(ThemeTable).all()


Base.metadata.create_all()
