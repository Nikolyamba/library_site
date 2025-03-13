import uuid

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from database import Base

class Genre(Base):
    __tablename__ = "genres"
    id = Column(String(), primary_key=True, default=lambda: str(uuid.uuid4()))
    genre_name = Column(String(36), unique=True, nullable=False)
    books = relationship("Book", secondary='book_genre_association', back_populates="genres")
    comments = relationship("Comment", back_populates="genre")


class BookGenreAssociation(Base):
    __tablename__ = 'book_genre_association'
    book_id = Column(String(), ForeignKey('books.id'), primary_key=True)
    genre_id = Column(String(), ForeignKey('genres.id'), primary_key=True)