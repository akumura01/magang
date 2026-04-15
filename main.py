from services.sentiment_service import sentiment_service
from models import EntityRecord
from fastapi import FastAPI
from pydantic import BaseModel
from database import SessionLocal
from models import SentimentRecord
from datetime import datetime

app = FastAPI()

from database import engine
from models import Base

Base.metadata.create_all(bind=engine)

class TextInput(BaseModel):
    text: str

@app.get("/")
def home():
    return {"message": "Sentiment API is running"}

@app.post("/projects/{project_id}/analyze")
def analyze(project_id: str, input: TextInput):

    analysis = sentiment_service.analyze(input.text)

    sentiment = analysis["sentiment"]
    confidence = analysis["confidence"]
    entities = analysis["entities"]

    db = SessionLocal()

    existing = db.query(SentimentRecord).filter(
    SentimentRecord.text == input.text,
    SentimentRecord.project_id == project_id
).first()

    if existing:
        db.close()
        return {
            "message": "duplicate data skipped",
            "text": input.text
        }

    record = SentimentRecord(
        text=input.text,
        sentiment=sentiment,
        confidence=confidence,
        timestamp=str(datetime.now()),
        project_id=project_id

    )

    db.add(record)

    for ent in entities:
        entity_record = EntityRecord(
            text=ent["text"],
            label=ent["label"],
            sentiment=sentiment,
            source_text=input.text,
            project_id=project_id
)
        db.add(entity_record)

    db.commit()
    db.close()

    return {
        "text": input.text,
        "sentiment": sentiment,
        "confidence": confidence,
        "entities": entities
    }

@app.get("/data")
def get_data(sentiment: str = None, limit: int = 10):
    db = SessionLocal()

    query = db.query(SentimentRecord)

    # Filter by sentiment if provided
    if sentiment:
        query = query.filter(SentimentRecord.sentiment == sentiment)

    # Order by latest data
    records = query.order_by(SentimentRecord.id.desc()).limit(limit).all()

    db.close()

    return records
@app.get("/entity")
def get_entity_sentiment(name: str):
    db = SessionLocal()

    records = db.query(EntityRecord).filter(
        EntityRecord.text.ilike(f"%{name}%")
    ).all()

    db.close()

    if not records:
        return {"message": "No data found"}

    summary = {
        "positive": 0,
        "neutral": 0,
        "negative": 0
    }

    for r in records:
        if r.sentiment in summary:
            summary[r.sentiment] += 1

    return {
        "entity": name,
        "total_mentions": len(records),
        "sentiment_summary": summary,
        "data": records[:10]  # sample data
    }
from collections import defaultdict

@app.get("/top-entities")
def get_top_entities(limit: int = 10):
    db = SessionLocal()

    records = db.query(EntityRecord).all()
    db.close()

    entity_map = {}

    for r in records:
        name = r.text.lower()

        if name not in entity_map:
            entity_map[name] = {
                "name": r.text,
                "total": 0,
                "positive": 0,
                "neutral": 0,
                "negative": 0
            }

        entity_map[name]["total"] += 1

        if r.sentiment in entity_map[name]:
            entity_map[name][r.sentiment] += 1

    # Convert to list
    result = list(entity_map.values())

    # Sort by total mentions
    result = sorted(result, key=lambda x: x["total"], reverse=True)

    return result[:limit]

@app.get("/projects/{project_id}/data")
def get_project_data(project_id: str, sentiment: str = None, limit: int = 10):
    db = SessionLocal()

    query = db.query(SentimentRecord).filter(
        SentimentRecord.project_id == project_id
    )

    if sentiment:
        query = query.filter(SentimentRecord.sentiment == sentiment)

    records = query.order_by(SentimentRecord.id.desc()).limit(limit).all()

    db.close()

    return records

@app.get("/projects/{project_id}/entity")
def get_project_entity_sentiment(project_id: str, name: str):
    db = SessionLocal()

    records = db.query(EntityRecord).filter(
        EntityRecord.project_id == project_id,
        EntityRecord.text.ilike(f"%{name}%")
    ).all()

    db.close()

    if not records:
        return {"message": "No data found"}

    summary = {
        "positive": 0,
        "neutral": 0,
        "negative": 0
    }

    for r in records:
        if r.sentiment in summary:
            summary[r.sentiment] += 1

    return {
        "project_id": project_id,
        "entity": name,
        "total_mentions": len(records),
        "sentiment_summary": summary,
        "data": records[:10]
    }

@app.get("/projects/{project_id}/top-entities")
def get_top_entities(project_id: str, limit: int = 10):
    db = SessionLocal()

    records = db.query(EntityRecord).filter(
        EntityRecord.project_id == project_id
    ).all()

    db.close()

    entity_map = {}

    for r in records:
        name = r.text.lower()

        if name not in entity_map:
            entity_map[name] = {
                "name": r.text,
                "total": 0,
                "positive": 0,
                "neutral": 0,
                "negative": 0
            }

        entity_map[name]["total"] += 1

        if r.sentiment in entity_map[name]:
            entity_map[name][r.sentiment] += 1

    result = list(entity_map.values())
    result = sorted(result, key=lambda x: x["total"], reverse=True)

    return result[:limit]
