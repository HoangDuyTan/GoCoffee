from django.urls import path
from . import views

urlpatterns = [
    # Trang chủ
    path('', views.home_view, name='home'),

    # Trang Lọc/Khám phá
    path('shops/', views.shop_list_view, name='shop_list'),

    # Trang Chi tiết về quán
    path('shop/<int:shop_id>/', views.shop_detail_view, name='shop_detail'),

    # Trang liên hệ
    path('contact/', views.contact_view, name='contact'),
]