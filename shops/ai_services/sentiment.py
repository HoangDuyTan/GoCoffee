import os
import re
import joblib
from django.conf import settings
from underthesea import word_tokenize

class SentimentEngine:
    _instance = None
    MODEL_PATH = os.path.join(settings.BASE_DIR, 'shops', 'ai_models')
    ASPECT_PATH = os.path.join(MODEL_PATH, 'model_aspect.pkl')
    SENTIMENT_PATH = os.path.join(MODEL_PATH, 'model_sentiment.pkl')

    BOOST_WORDS = {"rất":1.2, "cực kỳ":1.3, "siêu":1.3, "hơi":0.8, "khá":0.9}

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.model_aspect = None
        self.model_sentiment = None
        self.is_ready = False
        self._load_model()

    def _load_model(self):
        if not os.path.exists(self.ASPECT_PATH) or not os.path.exists(self.SENTIMENT_PATH):
            print(f"Không tìm thấy model tại {self.MODEL_PATH}")
            return

        try:
            self.model_aspect = joblib.load(self.ASPECT_PATH)
            self.model_sentiment = joblib.load(self.SENTIMENT_PATH)
            self.is_ready = True
            print(f"AI Sentiment of Aspect đã sẵn sàng")
        except Exception as e:
            print(f"Lỗi loading model: {e}")

    def analyze_sentiment(self, review):
        if not self.is_ready or not review:
            return self._result()

        try:
            split_pattern = (
                r'[.,;\n!+\-]|'
                r'\bnhưng\b|\btuy nhiên\b|\bsong\b|'
                r'\bvà\b|\bvới\b|\brồi\b|\bxong\b|\bthêm\b|\bcộng\b|\blẫn\b|\blại\b|'
                r'\bmà\b|\bcòn\b'
            )
            sentences = re.split(split_pattern, review.lower())
            final_scores = {'service': 0, 'ambiance': 0, 'drink': 0, 'price': 0}

            for sentence in sentences:
                if len(sentence.strip()) < 2:
                    continue

                processed_sentence = word_tokenize(sentence.strip(), format="text")
                input_data = [processed_sentence]

                # Dự đoán aspect
                aspect_probs = self.model_aspect.predict_proba(input_data)[0]
                predicted_aspect = self.model_aspect.predict(input_data)[0]
                if max(aspect_probs) < 0.6:
                    continue

                # Dự đoán sentiment
                sentiment_probs = self.model_sentiment.predict_proba(input_data)[0]
                predicted_sentiment = int(self.model_sentiment.predict(input_data)[0])
                confidence = max(sentiment_probs)

                # Tính weighted score
                weighted_score = predicted_sentiment * confidence

                # Boost từ khóa
                for word, factor in self.BOOST_WORDS.items():
                    if word in processed_sentence:
                        weighted_score *= factor

                if predicted_aspect in final_scores:
                    final_scores[predicted_aspect] += weighted_score

            for key in final_scores:
                if final_scores[key] > 0.5:
                    final_scores[key] = 1
                elif final_scores[key] < -0.5:
                    final_scores[key] = -1
                else:
                    final_scores[key] = 0

            return {f'sentiment_{k}': v for k, v in final_scores.items()}

        except Exception as e:
            print(f"Lỗi: {e}")
            return self._result()

    def _result(self):
        return {'sentiment_service': 0,
                'sentiment_ambiance': 0,
                'sentiment_drink': 0,
                'sentiment_price': 0}