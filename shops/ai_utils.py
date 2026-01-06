from .ai_services.sentiment import SentimentEngine
from .ai_services.recommender import RecommenderEngine

def analyze_review_sentiment(review):
    engine = SentimentEngine.get_instance()
    return engine.analyze_sentiment(review)

def analyze_collaboration_recommendation(user_id):
    engine = RecommenderEngine()
    return engine.get_collaboration_recommendation(user_id)