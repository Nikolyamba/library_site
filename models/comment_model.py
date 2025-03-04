from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship

from database import Base

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer(), ForeignKey('users.id'), nullable=False)
    target_user_id = Column(Integer(), ForeignKey('users.id'), nullable=True)
    book_id = Column(Integer(), ForeignKey('books.id'), nullable=True)
    author_id = Column(Integer(), ForeignKey('authors.id'), nullable=True)
    genre_id = Column(Integer(), ForeignKey('genres.id'), nullable=True)
    content = Column(String(), nullable=False)

    user = relationship("User", back_populates="comments")
    target_user = relationship("User", foreign_keys=[target_user_id], back_populates="received_comments")
    book = relationship("Book", back_populates="comments")
    author = relationship("Author", back_populates="comments")
    genre = relationship("Genre", back_populates="comments")


