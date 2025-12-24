import os
import re
import torch
from django.conf import settings
from transformers import AutoTokenizer, AutoModelForSequenceClassification


class SentimentEngine:
    _instance = None
    MODEL_PATH = os.path.join(settings.BASE_DIR, 'shops', 'ai_models', 'vietnamese_sentiment')

    # Tiết kiệm RAM
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.device = torch.device("cpu")
        self.tokenizer = None
        self.model = None
        self.is_ready = False

        self.keywords = {
            'drink': ['nước', 'uống', 'trà', 'cà phê', 'cafe', 'vị', 'ngon', 'dở', 'menu'],
            'service': ['phục vụ', 'nhân viên', 'thái độ', 'order', 'chờ', 'lâu', 'nhanh'],
            'price': ['giá', 'tiền', 'đắt', 'rẻ', 'bill', 'hóa đơn', 'mắc'],
            'ambiance': ['không gian', 'view', 'ồn', 'nhạc', 'trang trí', 'đẹp', 'xấu', 'mát', 'nóng']
        }
        self._load_model()

    def _load_model(self):
        if not os.path.exists(self.MODEL_PATH):
            print(f"Không tìm thấy model tại {self.MODEL_PATH}")
            return

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.MODEL_PATH, local_files_only=True)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.MODEL_PATH, local_files_only=True)
            self.model.to(self.device)
            self.is_ready = True
            print(f"AI Sentiment of Aspect đã sẵn sàng")
        except Exception as e:
            print(f"Lỗi loading model: {e}")

    def analyze_sentiment(self, review):
        if not self.is_ready or not review:
            return self._result()

        try:
            sentences = re.split(r'[.,;\n!]\s*', review)
            final_scores = {'service': 0, 'ambiance': 0, 'drink': 0, 'price': 0}

            for sentence in sentences:
                if len(sentence.strip()) < 2:
                    continue

                sentiment_val = self._predict_one_sentence(sentence)
                if sentiment_val == 0:
                    continue

                detected_aspect = self._detect_aspect(sentence)

                for aspect in detected_aspect:
                    final_scores[aspect] += sentiment_val

            return {f'sentiment_{k}': v for k, v in final_scores.items()}

        except Exception as e:
            print(f"Lỗi: {e}")
            return self._result()

    def _predict_one_sentence(self, text):
        inputs = self.tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=256)

        with torch.no_grad():
            outputs = self.model(**inputs)

        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        label_id = torch.argmax(probs).item()

        if label_id == 0:
            return -1
        if label_id == 1:
            return 1
        return 0

    def _detect_aspect(self, text):
        text = text.lower()
        found = []
        for aspect, keywords in self.keywords.items():
            if any(kw in text for kw in keywords):
                found.append(aspect)
        return found

    def _result(self):
        return {'sentiment_service': 0,
                'sentiment_ambiance': 0,
                'sentiment_drink': 0,
                'sentiment_price': 0}