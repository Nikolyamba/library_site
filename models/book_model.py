from sqlalchemy import Integer, Column, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from database import Base

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    title = Column(String(50), unique=False, nullable=False)
    year = Column(Integer(), nullable=False)
    pages = Column(Integer(), nullable=False)
    profile_picture = Column(String(200), unique=False, nullable=False)
    country = Column(String(25), unique=False, nullable=False)
    author_id = Column(Integer(), ForeignKey("authors.id"))
    average_rating = Column(Float(), unique=False, nullable=True)

    author = relationship("Author", back_populates="books")
    genres = relationship("Genre", secondary='book_genre_association', back_populates="books")
    comments = relationship("Comment", back_populates="book")
    readers = relationship("UserBook", back_populates="book")

class UserBook(Base):
    __tablename__ = "user_books"
    user_id = Column(Integer(), ForeignKey('users.id'), primary_key=True)
    book_id = Column(Integer(), ForeignKey('books.id'), primary_key=True)
    rating = Column(Integer(), nullable = True)

    user = relationship("User", back_populates="readed_books")
    book = relationship("Book", back_populates="readers")
