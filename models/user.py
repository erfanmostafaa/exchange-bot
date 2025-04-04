from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import DateTime
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    name = Column(String, nullable=False)
    national_number = Column(String(10), nullable=False)
    phone = Column(String(20), nullable=True)
    requests = relationship("Request", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, user_id={self.user_id}, name={self.name})>"


class Request(Base):
    __tablename__ = 'requests'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False) 
    currency = Column(String, nullable=False)
    transaction_type = Column(String, nullable=False)
    payment_method = Column(String, nullable=False) 
    entity_type = Column(String, nullable=False)
    country = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)  
    price = Column(Float, nullable=False)  
    created_at = Column(DateTime, default=datetime.now)
    user = relationship("User", back_populates="requests")

    def __repr__(self):
        return f"<Request(id={self.id}, user_id={self.user_id}, currency={self.currency})>"