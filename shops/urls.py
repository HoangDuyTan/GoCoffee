from django.contrib import admin
from django.urls import path, include
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

    # Trang Dành cho bạn
    path('foryou/', views.for_you_view, name='for_you'),

    # Chức năng đăng nhập
    path('users/', include('users.urls')),

    # Map API
    path("api/shops/map/", views.shop_map_api, name="shop_map_api"),

    # Chức năng Review
    path('shop/<int:shop_id>/review/', views.submit_review, name='submit_review'),
]
