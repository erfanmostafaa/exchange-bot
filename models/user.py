from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    name = Column(String, nullable=False)
    national_number = Column(String(10), nullable=False)
    phone = Column(String(11), nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, user_id={self.user_id}, name={self.name})>"
