from sqlalchemy import Column, Integer, String, Float
from database import Base

class SentimentRecord(Base):
    __tablename__ = "sentiments"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    sentiment = Column(String)
    confidence = Column(Float)
    timestamp = Column(String)

    project_id = Column(String, index=True)


class EntityRecord(Base):
    __tablename__ = "entities"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    label = Column(String)
    sentiment = Column(String)
    source_text = Column(String)

    project_id = Column(String, index=True)