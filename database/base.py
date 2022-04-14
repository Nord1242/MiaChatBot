from sqlalchemy.orm import declarative_base
from loader import engine, metadata

Base = declarative_base(bind=engine, metadata=metadata)
