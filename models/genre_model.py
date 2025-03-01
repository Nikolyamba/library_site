from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from database import Base

class Genre(Base):
    __tablename__ = "genres"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    genre_name = Column(String(36), unique=True, nullable=False)
    books = relationship("Book", secondary='book_genre_association', back_populates="genres")


class BookGenreAssociation(Base):
    __tablename__ = 'book_genre_association'
    book_id = Column(Integer, ForeignKey('books.id'), primary_key=True)
    genre_id = Column(Integer, ForeignKey('genres.id'), primary_key=True)