from models import EntityRecord
import spacy 
nlp = None

def load_nlp():
    global nlp
    if nlp is None:
        print("Loading NLP model...")
        nlp = spacy.load("xx_ent_wiki_sm")

from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline
from database import SessionLocal
from models import SentimentRecord
from datetime import datetime

app = FastAPI()

from database import engine
from models import Base

Base.metadata.create_all(bind=engine)

# Load sentiment model
classifier = pipeline(
    "sentiment-analysis",
    model="nlptown/bert-base-multilingual-uncased-sentiment"
)

class TextInput(BaseModel):
    text: str

@app.get("/")
def home():
    return {"message": "Sentiment API is running"}

def convert_sentiment(label):
    
    stars = int(label[0])  # "1 star" → 1

    if stars <= 2:
        return "negative"
    elif stars == 3:
        return "neutral"
    else:
        return "positive"
    
def extract_entities(text):
    load_nlp()  # 👈 important

    doc = nlp(text)
    entities = []

    for ent in doc.ents:
        entities.append({
            "text": ent.text,
            "label": ent.label_
        })

    return entities

@app.post("/analyze")
def analyze(input: TextInput):
    result = classifier(input.text)[0]
    sentiment = convert_sentiment(result["label"])
    entities = extract_entities(input.text)
    db = SessionLocal()

    # 🔴 CHECK DUPLICATE
    existing = db.query(SentimentRecord).filter(SentimentRecord.text == input.text).first()

    if existing:
        db.close()
        return {
            "message": "duplicate data skipped",
            "text": input.text
        }

    # ✅ INSERT IF NEW
    record = SentimentRecord(
        text=input.text,
        sentiment=sentiment,
        confidence=result["score"],
        timestamp=str(datetime.now())
    )
    db.add(record)
    # 🔹 Save entities
    for ent in entities:
        entity_record = EntityRecord(
        text=ent["text"],
        label=ent["label"],
        sentiment=sentiment,
        source_text=input.text
    )
    db.add(entity_record)
    db.commit()
    db.close()

    return {
    "text": input.text,
    "sentiment": sentiment,
    "confidence": result["score"],
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