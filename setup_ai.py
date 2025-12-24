import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH = os.path.join(BASE_DIR, 'shops', 'ai_models', 'vietnamese_sentiment')
MODEL_NAME = 'wonrax/phobert-base-vietnamese-sentiment'

def download_model():
    print('Downloading model...')
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

        tokenizer.save_pretrained(SAVE_PATH)
        model.save_pretrained(SAVE_PATH)
        print('Model downloaded.')
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == '__main__':
    download_model()