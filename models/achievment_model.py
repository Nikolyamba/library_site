from sqlalchemy import Integer, Column, String
from database import Base

class Achievment(Base):
    __tablename__ = "achievments"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    a_name = Column(String(50), unique=True, nullable=False)
    target = Column(Integer(), nullable=False)