from sqlalchemy import Integer, Column, String, Float
from sqlalchemy.orm import relationship
from database import Base

class Author(Base):
    __tablename__ = "authors"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(36), unique=False, nullable=False)
    surname = Column(String(36), unique=False, nullable=False)
    patronymic = Column(String(36), unique=False, nullable=True)
    country = Column(String(36), unique=False, nullable=True)
    profile_picture = Column(String(200), unique=False, nullable=False)
    average_rating = Column(Float(), unique=False, nullable=True)

    books = relationship("Book", back_populates="author")
    comments = relationship("Comment", back_populates="author")