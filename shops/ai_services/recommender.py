import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from django.db.models import Case, When
from shops.models import CafeShop, Review, ShopViewLog

class RecommenderEngine:
    def __init__(self):
        self.top_k_users = 5
        self.top_n_items = 8

    def get_collaboration_recommendation(self, user_id):
        # 1. Lấy ra ma trận
        user_item_matrix = self._get_interaction_matrix()
        if user_item_matrix is None or user_id not in user_item_matrix.index or user_item_matrix.empty:
            return []

        # 2. Tính độ tương đồng
        user_similar_matrix = cosine_similarity(user_item_matrix)
        user_similar_df = pd.DataFrame(user_similar_matrix, index=user_item_matrix.index,
                                       columns=user_item_matrix.index)

        # 3. Tìm 5 user khác có cùng độ tương đồng cao nhất
        similar_users = user_similar_df[user_id].sort_values(ascending=False).drop(user_id).head(self.top_k_users)
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

        rec_shop_ids = recommendation_scores.head(self.top_n_items).index.tolist()
        if not rec_shop_ids:
            return []

        preserved_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(rec_shop_ids)])
        return CafeShop.objects.filter(pk__in=rec_shop_ids).order_by(preserved_order)


    def _get_interaction_matrix(self):
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