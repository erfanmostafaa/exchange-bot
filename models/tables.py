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
    phone_number = Column(String(20), nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, user_id={self.user_id}, name={self.name})>"


class Remittance(Base):
    __tablename__ = 'remittance'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False) 
    currency = Column(String, nullable=False)
    transaction_type = Column(String, nullable=False)
    payment_method = Column(String, nullable=False) 
    entity_type = Column(String, nullable=False)
    country = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)  
    price = Column(Float, nullable=False)  
    remittance_id = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Remittance(id={self.id}, user_id={self.user_id}, currency={self.currency})>"