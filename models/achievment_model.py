import uuid

from sqlalchemy import Integer, Column, String, ForeignKey
from sqlalchemy.orm import relationship

from database import Base

class Achievment(Base):
    __tablename__ = "achievments"
    id = Column(String(), primary_key=True, default=lambda: str(uuid.uuid4()))
    a_name = Column(String(50), unique=True, nullable=False)
    target = Column(Integer(), unique=False, nullable=False)
    genre_id = Column(String(), nullable=True)

    users = relationship("User", secondary='user_achiev_association', back_populates="achievments")

class UserAchievAssociation(Base):
    __tablename__ = 'user_achiev_association'
    user_id = Column(String(), ForeignKey('users.id'), primary_key=True)
    achievment_id = Column(String(), ForeignKey('achievments.id'), primary_key=True)

    user = relationship("User", back_populates="achievments")
    achievment = relationship("Achievment", back_populates="users")