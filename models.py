from sqlalchemy import Column, Integer, String, Float
from database import Base

class SentimentRecord(Base):
    __tablename__ = "sentiments"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    sentiment = Column(String)
    confidence = Column(Float)
    timestamp = Column(String)


# 👇 ADD THIS
class EntityRecord(Base):
    __tablename__ = "entities"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)          # entity name
    label = Column(String)         # PER, ORG, etc.
    sentiment = Column(String)     # link sentiment
    source_text = Column(String)   # original sentence