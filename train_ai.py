from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.svm import SVC
import os
import joblib

from underthesea import word_tokenize
from training_data import TRAIN_DATA


def train_and_save():
    print("Đang bắt đầu dạy AI học...")

    processed_texts = []
    for item in TRAIN_DATA:
        raw_text = item[0]
        tokenized_text = word_tokenize(raw_text.lower(), format="text")
        processed_texts.append(tokenized_text)

    aspect_label = [item[1] for item in TRAIN_DATA]
    sentiment_labels = [item[2] for item in TRAIN_DATA]

    model_aspect = make_pipeline(
        TfidfVectorizer(ngram_range=(1, 3), min_df=2, max_df=0.85, sublinear_tf=True),
        SVC(kernel='linear', probability=True, C=2.0, class_weight='balanced'),
    )
    model_aspect.fit(processed_texts, aspect_label)
    print("Đã học xong phần chủ đề (Aspect)")

    model_sentiment = make_pipeline(
        TfidfVectorizer(ngram_range=(1, 3), min_df=2, max_df=0.85, sublinear_tf=True),
        SVC(kernel='linear', probability=True, C=2.0, class_weight='balanced'),
    )
    model_sentiment.fit(processed_texts, sentiment_labels)
    print("Đã học xong phần cảm xúc (Sentiment)")

    save_dir = 'shops/ai_models'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    joblib.dump(model_aspect, os.path.join(save_dir, 'model_aspect.pkl'))
    joblib.dump(model_sentiment, os.path.join(save_dir, 'model_sentiment.pkl'))
    print(f"Đã lưu 2 file vào: {save_dir}")


if __name__ == "__main__":
    train_and_save()
