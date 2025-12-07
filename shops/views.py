from django.shortcuts import render, get_object_or_404
from .models import CafeShop
from django.db.models import Avg, Count
# Create your views here.
def home_view(request):
    hot_shop = CafeShop.objects.all()[:3]
    new_shop = CafeShop.objects.all().order_by('-id')[:3]
    popular_shop = CafeShop.objects.all().order_by('?')[:3]
    context = {
        'new_shop': new_shop,
        'hot_shop': hot_shop,
        'popular_shop': popular_shop
    }
    return render(request, 'home.html', context)

def shop_list_view(request):
    shops = CafeShop.objects.all()
    context = {
        'shops': shops
    }
    return render(request, 'shop_list.html', context)

def shop_detail_view(request, shop_id):
    shop = get_object_or_404(CafeShop, pk=shop_id)
    context = {
        'shop': shop
    }
    return render(request, 'shop_detail.html', context)

def contact_view(request):
    return render(request, 'contact.html')


def shop_detail_view(request, shop_id):
    # 1. Lấy Shop và tính toán Rating/Review
    # Dùng related_name='reviews'
    shop = get_object_or_404(
        CafeShop.objects
        .annotate(
            rating_avg=Avg('reviews__rating'),
            review_count=Count('reviews')
        ),
        pk=shop_id
    )

    # 2. Xử lý Menu: Nhóm các món theo Danh mục
    # Dùng related_name='menu_items'
    menu_items = shop.menu_items.all().order_by('category', 'id')

    grouped_menu = {}
    for item in menu_items:
        category = item.category if item.category else "Menu chung"
        if category not in grouped_menu:
            grouped_menu[category] = []

        # Format giá (Giữ nguyên logic format string)
        price_formatted = f"{item.price:,.0f}₫".replace(",", "tmp").replace(".", ",").replace("tmp", ".")

        grouped_menu[category].append({
            'name': item.name,
            'price': price_formatted
        })

    # 3. Lấy đánh giá, sắp xếp mới nhất lên trước
    reviews = shop.reviews.all().select_related('user').order_by('-created_at')

    # 4. Lấy 3 quán liên quan
    related_shops = CafeShop.objects.filter(district=shop.district).exclude(pk=shop_id)[:3]

    # 5. Kiểm tra xem người dùng đã lưu quán này chưa
    # Phải import SavedShop nếu bạn muốn kiểm tra (tạm thời không cần vì không hiển thị)

    context = {
        'shop': shop,
        'grouped_menu': grouped_menu,
        'reviews': reviews,
        'related_shops': related_shops,


    }

    return render(request, 'shop_detail.html', context)