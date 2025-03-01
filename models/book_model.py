from sqlalchemy import Integer, Column, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    title = Column(String(50), unique=False, nullable=False)
    year = Column(Integer(), nullable=True)
    pages = Column(Integer(), nullable=True)
    profile_picture = Column(String(200), unique=False, nullable=False)
    author_id = Column(Integer(), ForeignKey("authors.id"))
    author = relationship("Author", back_populates="books")
    genres = relationship("Genre", secondary='book_genre_association', back_populates="books")
