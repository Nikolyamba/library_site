import uuid

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship

from database import Base

class Comment(Base):
    __tablename__ = "comments"

    id = Column(String(), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(), ForeignKey('users.id'), nullable=False)
    target_user_id = Column(String(), ForeignKey('users.id'), nullable=True)
    book_id = Column(String(), ForeignKey('books.id'), nullable=True)
    author_id = Column(String(), ForeignKey('authors.id'), nullable=True)
    genre_id = Column(String(), ForeignKey('genres.id'), nullable=True)
    content = Column(String(), nullable=False)

    user = relationship("User", foreign_keys=[user_id], back_populates="comments")
    target_user = relationship("User", foreign_keys=[target_user_id], back_populates="received_comments")
    book = relationship("Book", back_populates="comments")
    author = relationship("Author", back_populates="comments")
    genre = relationship("Genre", back_populates="comments")


