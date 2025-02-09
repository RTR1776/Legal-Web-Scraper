from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    jurisdiction = Column(String, index=True)
    document_type = Column(String, index=True)
    title = Column(String)
    metadata = Column(JSON)
    content = Column(Text)
    source_url = Column(String, unique=True, index=True)
    date_scraped = Column(DateTime, default=datetime.datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="user")  # Either "user" or "admin"