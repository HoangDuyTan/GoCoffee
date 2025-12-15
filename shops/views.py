from django.shortcuts import render, get_object_or_404, redirect

from .models import CafeShop, Contact
from django.db.models import Avg, Count
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse

# Create your views here.
def home_view(request):
    hot_shop = CafeShop.objects.all()[:10]
    new_shop = CafeShop.objects.all().order_by('-id')[:10]
    popular_shop = CafeShop.objects.all().order_by('?')[:10]
    context = {
        'new_shop': new_shop,
        'hot_shop': hot_shop,
        'popular_shop': popular_shop
    }
    return render(request, 'home.html', context)

def filtered_shops(request):
    shops = CafeShop.objects.all().order_by('-id')

    #search
    query = request.GET.get('search')
    if query:
        shops = shops.filter(
            Q(name__icontains=query) |
            Q(address__icontains=query) |
            Q(tags__icontains=query)
        )

    #filtered district
    district = request.GET.get('district')
    if district:
        shops = shops.filter(district=district)

    rating = request.GET.get('rating', '0')

    if rating:
        try:
            rating = float(rating)
        except ValueError:
            rating = 0
        if rating > 0:
            shops = shops.filter(rating=rating)

    tags = request.GET.getlist('tags[]')
    if tags:
        query = Q()
        for tag in tags:
            query |= Q(tags__icontains=tag)
        shops = shops.filter(query)

    price_range = request.GET.get('price_range')
    if price_range:
        filtered_shops = []

        for shop in shops:
            min_price = shop.get_min_price()
            max_price = shop.get_max_price()

            if price_range == 'under_50' and max_price and max_price <= 50000:
                filtered_shops.append(shop)
            elif price_range == '50_80' and min_price and max_price:
                if min_price >= 50000 and max_price <= 80000:
                    filtered_shops.append(shop)
            elif price_range == 'over_80' and min_price and min_price >= 80000:
                filtered_shops.append(shop)
        shops = filtered_shops

    amenities = request.GET.getlist('amenities[]')
    if amenities:
        query = Q()
        for amenity in amenities:
            query |= Q(amenities__icontains=amenity)
        shops = shops.filter(query)

    return shops, district, rating, tags, price_range, amenities

def shop_list_view(request):
    shops, district, rating, tags, price_range, amenities = filtered_shops(request)
    paginator = Paginator(shops, 8)
    page_number = request.GET.get('page')
    context = {
        'shops': paginator.get_page(page_number),
        'selected_district': district,
        'rating': rating,
        'selected_tags': tags,
        'selected_price_range': price_range,
        'selected_amenities': amenities
    }
    return render(request, 'shop_list.html', context)
def shop_map_api(request):
    shops, _, _, _, _, _ = filtered_shops(request)
    data = [
        {
            'name': shop.name,
            'lat': shop.latitude,
            'lng': shop.longitude,
            'rating': shop.rating,
            'address': shop.address,
            'cover_image': shop.cover_image.url if shop.cover_image else '',
        }
        for shop in shops
        if shop.latitude and shop.longitude
    ]

    return JsonResponse(data, safe=False)

def shop_detail_view(request, shop_id):
    shop = get_object_or_404(CafeShop, pk=shop_id)
    context = {
        'shop': shop
    }
    return render(request, 'shop_detail.html', context)

def contact_view(request):

    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        email = request.POST.get('email')
        topic = request.POST.get('topic')
        content = request.POST.get('content')

        try:
            Contact.objects.create(
                fullname=fullname,
                email=email,
                topic=topic,
                content=content
            )

            return redirect('contact')

        except Exception as e:
            print(f"Lỗi khi lưu Contact: {e}")
            pass


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