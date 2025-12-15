# underthesea: cắt từ tiếng Việt
# scikit-learn: tính độ tương đồng
# pandas: xử lý bảng dữ liệu
# numpy: tính toán số học

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from underthesea import word_tokenize
from .models import CafeShop, Review, ShopViewLog
from django.db.models import Case, When

# ====== SEGMENT OF ASPECT ======
aspect_keyword = {
    'service': {'phục vụ', 'phục_vụ', 'nhân viên', 'nhân_viên', 'thái độ', 'thái_độ', 'bảo vệ', 'bảo_vệ', 'giữ xe',
                'giữ_xe', 'order', 'lên món', 'lên_món', 'chủ quán', 'chủ_quán', 'bill', 'thanh toán', 'thanh_toán',
                'staff', 'nhan_vien', 'lễ tân', 'lễ_tân', 'waiter'},
    'ambiance': {'không gian', 'không_gian', 'view', 'decor', 'trang trí', 'trang_trí',
                 'chỗ ngồi', 'chỗ_ngồi', 'ồn', 'yên tĩnh', 'yên_tĩnh', 'nhạc', 'đẹp',
                 'thoáng', 'điều hòa', 'điều_hòa', 'máy lạnh', 'máy_lạnh', 'wc', 'nhà vệ sinh',
                 'check in', 'check_in', 'sống ảo', 'sống_ảo', 'background'},
    'drink': {'nước', 'cà phê', 'cà_phê', 'trà', 'bánh', 'menu', 'vị', 'ngon', 'dở',
              'uống', 'đồ uống', 'đồ_uống', 'nước uống', 'nước_uống', 'cafe', 'coffee',
              'topping', 'trân châu', 'trân_châu', 'đá xay', 'đá_xay'},
    'price': {'giá', 'giá_cả', 'mắc', 'rẻ', 'chi phí', 'chi_phí', 'tiền', 'ví',
              'bill', 'tổng thiệt hại', 'đắt'}
}

sentiment_word = {
    'positive': {'ngon', 'tốt', 'đẹp', 'tuyệt', 'thích', 'ok', 'ổn', 'hài lòng', 'hài_lòng',
                 'rẻ', 'hợp lý', 'hợp_lý', 'dễ thương', 'dễ_thương', 'nhanh', 'thoáng',
                 'vui', 'xuất sắc', 'xuất_sắc', 'đỉnh', 'chất lượng', 'chất_lượng',
                 'phê', 'mlem', 'thơm', 'sạch', 'sạch_sẽ', 'nice', 'good'},
    'negative': {'dở', 'tệ', 'xấu', 'chán', 'đắt', 'mắc', 'chậm', 'thái độ', 'thái_độ',
                 'ồn', 'dơ', 'bẩn', 'nhạt', 'đau', 'lồi lõm', 'lồi_lõm', 'cọc',
                 'khó chịu', 'khó_chịu', 'hôi', 'gắt', 'chát', 'ngu', 'tệ_hại'},
    'negation': {'không', 'chẳng', 'chả', 'kém', 'chưa', 'đừng', 'khong', 'chang', 'ko', 'not'}
}


def analyze_review_sentiment(review):
    if not review:
        return {'sentiment_service': 0, 'sentiment_ambiance': 0, 'sentiment_drink': 0, 'sentiment_price': 0}
    review = review.lower()
    try:
        tokens = word_tokenize(review)
    except:
        tokens = review.split()

    score = {
        'service': 0,
        'ambiance': 0,
        'drink': 0,
        'price': 0
    }

    # Quét qua từng từ trong câu
    for i, word in enumerate(tokens):
        found_aspect = None
        for aspect, keyword in aspect_keyword.items():
            if word in keyword:
                found_aspect = aspect
                break

        if found_aspect is not None:
            start = max(0, i - 4)
            end = min(len(tokens), i + 5)
            context = tokens[start:end]

            local_score = 0
            has_negation = False

            for w in context:
                if w in sentiment_word['negation']:
                    has_negation = True
                elif w in sentiment_word['positive']:
                    local_score = 1
                elif w in sentiment_word['negative']:
                    local_score = -1

            if has_negation:
                local_score = -local_score

            # Ghi nhận lại điểm cho từng aspect
            if local_score != 0:
                score[found_aspect] = local_score

    return {
        'sentiment_service': score['service'],
        'sentiment_ambiance': score['ambiance'],
        'sentiment_drink': score['drink'],
        'sentiment_price': score['price']
    }

# ====== RECOMMENDATION SYSTEM ======
def get_collaboration_recommendation(user_id):
    # 1. Lấy ra ma trận
    user_item_matrix = get_interaction_matrix()
    if user_item_matrix is None or user_id not in user_item_matrix.index or user_item_matrix.empty:
        return []

    # 2. Tính độ tương đồng
    user_similar_matrix = cosine_similarity(user_item_matrix)
    user_similar_df = pd.DataFrame(user_similar_matrix, index=user_item_matrix.index, columns=user_item_matrix.index)

    # 3. Tìm 5 user khác có cùng độ tương đồng cao nhất
    similar_users = user_similar_df[user_id].sort_values(ascending=False).drop(user_id).head(5)
    similar_users = similar_users[similar_users > 0]
    if similar_users.empty:
        return []

    # 4. Lấy rating của các neighbor để tính điểm cho shop
    neighbor_rating = user_item_matrix.loc[similar_users.index]
    # Tính tổng điểm dọc theo cột (từng shop)
    weighted_score = neighbor_rating.multiply(similar_users, axis=0).sum(axis=0)

    # 5. Lọc quán
    # Những quán user đã xem
    watched_shops = user_item_matrix.loc[user_id]
    watched_shops = watched_shops[watched_shops > 0].index
    # Lọc quán chưa đi và xếp điểm từ cao xuống thấp
    recommendation_scores = weighted_score[~weighted_score.index.isin(watched_shops)]
    recommendation_scores = recommendation_scores[recommendation_scores > 0].sort_values(ascending=False)

    rec_shop_ids = recommendation_scores.head(8).index.tolist()
    if not  rec_shop_ids:
        return []

    preserved_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(rec_shop_ids)])
    return CafeShop.objects.filter(pk__in=rec_shop_ids).order_by(preserved_order)

def get_interaction_matrix():
    reviews = list(Review.objects.all().values('user_id', 'shop_id', 'rating'))
    views = list(ShopViewLog.objects.all().values('user_id', 'shop_id', 'view_count'))
    if not reviews and not views:
        return None

    if reviews:
        df_review = pd.DataFrame(reviews)
    else:
        df_review = pd.DataFrame(columns=['user_id', 'shop_id', 'rating'])

    if views:
        df_view = pd.DataFrame(views)
        df_view['rating'] = df_view['view_count'].apply(lambda x: min(x * 0.5, 4.0))
        df_view = df_view[['user_id', 'shop_id', 'rating']]
    else:
        df_view = pd.DataFrame(columns=['user_id', 'shop_id', 'rating'])

    df_total = pd.concat([df_review, df_view]).drop_duplicates(subset=['user_id', 'shop_id'], keep='first')
    return df_total.pivot_table(index='user_id', columns='shop_id', values='rating').fillna(0)