from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship

from database import Base

# class Comment(Base):
#     __tablename__ = "comments"
#     id = Column(Integer(), primary_key=True, autoincrement=True)
#     text = Column(Text(), unique=False, nullable=False)
#     user_id = Column(Integer, ForeignKey("users.id"))
#     user = relationship("User", back_populates="comments")


