from sqlalchemy import Column, Integer, String
from app.dependencies.database import Base

class Contact(Base):
    __tablename__ = "Contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(80), nullable=False, index=True)
    last_name = Column(String(80), nullable=False, index=True)
    phone = Column(String, unique=True, nullable=False, index=True)
    address = Column(String)
