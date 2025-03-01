from sqlalchemy import Integer, Column, String, Date, Boolean
from sqlalchemy.orm import relationship

from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer(), primary_key = True, autoincrement = True)
    login = Column(String(36), unique=True, nullable=False)
    password = Column(String(128), unique=False, nullable=False)
    name = Column(String(36), unique=False, nullable=True)
    surname = Column(String(36), unique=False, nullable=True)
    email = Column(String(), unique=True, nullable=False)
    birthday = Column(Date(), unique=False, nullable=True)
    sex = Column(String(10), unique=False, nullable=True)
    profile_picture = Column(String(200), unique=False, nullable=True)
    is_admin = Column(Boolean(), default=False, nullable=True)
    # comments = relationship("Comment", back_populates="users")

