from sqlalchemy import Column, Integer, String, Float, Date
from app.database import Base


class SalesTransaction(Base):
    __tablename__ = "sales_transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, index=True, nullable=False)
    order_date = Column(Date, nullable=False)
    product = Column(String, nullable=False)
    category = Column(String, nullable=False)
    region = Column(String, nullable=False)
    sales_channel = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    discount_amount = Column(Float, nullable=False, default=0.0)
    status = Column(String, nullable=False)
    net_revenue = Column(Float, nullable=False)
