from sqlalchemy import Column, String, Date, DECIMAL, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Customer(Base):
    __tablename__ = "customers"
    __table_args__ = {"schema": "public_staging"}

    customer_id = Column(String(50), primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(20))
    address = Column(String)
    date_of_birth = Column(Date)
    account_balance = Column(DECIMAL(15, 2))
    created_at = Column(TIMESTAMP)

    def to_dict(self):
        return {
            "customer_id": self.customer_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "date_of_birth": str(self.date_of_birth) if self.date_of_birth else None,
            "account_balance": float(self.account_balance) if self.account_balance is not None else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }