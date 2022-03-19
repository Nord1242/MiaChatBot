from sqlalchemy.orm import declarative_base
from loader import engine

Base = declarative_base(bind=engine)
