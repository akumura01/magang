from transformers import pipeline
import spacy

# Load models
classifier = pipeline(
    "sentiment-analysis",
    model="nlptown/bert-base-multilingual-uncased-sentiment"
)

nlp = spacy.load("xx_ent_wiki_sm")


class SentimentService:

    def convert_sentiment(self, label):
        stars = int(label[0])

        if stars <= 2:
            return "negative"
        elif stars == 3:
            return "neutral"
        else:
            return "positive"

    def extract_entities(self, text: str):
        doc = nlp(text)

        entities = []
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_
            })

        return entities

    def analyze(self, text: str):
        result = classifier(text)[0]

        sentiment = self.convert_sentiment(result["label"])
        entities = self.extract_entities(text)

        return {
            "sentiment": sentiment,
            "confidence": result["score"],
            "entities": entities
        }


# 🚨 THIS LINE IS REQUIRED
sentiment_service = SentimentService()