from sqlalchemy import Column , Integer , String , ForeignKey
from sqlalchemy.orm import relationship
from .user import Base


class Request(Base):
    __tablename__ = 'requests'

    id = Column(Integer , primary_key = True)
    user_id = Column(Integer , ForeignKey('user.user_id') , nullable= False)
    currency = Column(String, nullable=False)
    transaction_type = Column(String, nullable=False)
    payment_type = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    country = Column(String, nullable=False)
    amount = Column(String, nullable=False)

    user = relationship("User" , back_populates="requests")

    def __repr__(self):
        return f"<Request(id={self.id}, user_id={self.user_id}, currency={self.currency})>"