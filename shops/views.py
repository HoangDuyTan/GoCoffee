from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.http import JsonResponse
from django.contrib import messages
from .models import CafeShop, Contact, ShopViewLog, Review
from django.db.models import Avg, F, Count
from django.core.paginator import Paginator
from collections import Counter
from .ai_utils import analyze_review_sentiment, analyze_collaboration_recommendation
from collections import Counter
from .models import SavedShop


# Create your views here.
def home_view(request):
    hot_shops = CafeShop.objects.filter(rating__gte=4.0).order_by('-rating')[:10]
    new_shops = CafeShop.objects.all().order_by('-id')[:10]
    popular_shops = CafeShop.objects.annotate(review_count=Count('reviews')).order_by('-review_count')[:10]
    context = {
        'new_shop': new_shops,
        'hot_shop': hot_shops,
        'popular_shop': popular_shops
    }
    return render(request, 'home.html', context)


@login_required(login_url='/login/')
def for_you_view(request):
    user = request.user
    favorite_shops = CafeShop.objects.filter(
        savedshop__user=user
    ).distinct()

    # 1. LẤY DỮ LIỆU LỊCH SỬ
    viewed_shop_ids = ShopViewLog.objects.filter(user=user).values_list('shop_id', flat=True)
    viewed_shops = CafeShop.objects.filter(id__in=viewed_shop_ids)

    # 2. XÂY DỰNG USER PERSONA
    # tags
    all_tags = []
    for shop in viewed_shops:
        if shop.tags:
            tags_list = [t.strip() for t in shop.tags.split(',')]
            all_tags.extend(tags_list)

    if all_tags:
        most_common = Counter(all_tags).most_common(2)
        user_styles = [tag[0] for tag in most_common]
    else:
        user_styles = ["Đang tìm hiểu...", "Khám phá ngay"]

    # district
    most_viewed_district = ShopViewLog.objects.filter(user=user) \
        .values('shop__district').annotate(count=Count('id')).order_by('-count').first()

    favorite_district = most_viewed_district['shop__district'] if most_viewed_district else "Toàn thành phố"

    # price range
    price_range_display = "Mọi mức giá"
    if viewed_shops.exists():
        total_min = 0
        total_max = 0
        count = 0

        for shop in viewed_shops:
            mn = shop.get_min_price()
            mx = shop.get_max_price()
            if mn is not None and mx is not None:
                total_min += mn
                total_max += mx
                count += 1

        if count > 0:
            avg_min = total_min / count
            avg_max = total_max / count
            p_min = int(round(avg_min / 1000))
            p_max = int(round(avg_max / 1000))
            price_range_display = f"{p_min}k - {p_max}k"

    # 3. AI RECOMMENDATION
    ai_shops = analyze_collaboration_recommendation(user.id) or []

    if not ai_shops:
        if user_styles and user_styles[0] != "Đang tìm hiểu...":
            top_style = user_styles[0]
            ai_shops = list(CafeShop.objects.filter(tags__icontains=top_style)
                            .exclude(id__in=viewed_shop_ids).order_by('-rating')[:5])

        if not ai_shops:
            ai_shops = list(CafeShop.objects.filter(rating__gte=4.0).order_by('?')[:5])

    for index, shop in enumerate(ai_shops):
        if hasattr(shop, 'similarity') and shop.similarity > 0:
            shop.match_score = int(shop.similarity * 100)
        else:
            shop.match_score = None

        tags = []
        if getattr(shop, 'avg_ambiance', 0) > 0.6: tags.append('Không gian Chill')
        if getattr(shop, 'avg_service', 0) > 0.6: tags.append('Phục vụ tốt')
        if getattr(shop, 'avg_drink', 0) > 0.6: tags.append('Đồ uống ngon')
        if getattr(shop, 'avg_price', 0) > 0.6: tags.append('Giá hợp lý')

        # Nếu chưa đủ tag AI, lấy tag gốc
        if len(tags) < 2 and shop.tags:
            original_tags = [t.strip() for t in shop.tags.split(',')]
            remaining = [t for t in original_tags if t not in tags]
            tags.extend(remaining[:2 - len(tags)])

        shop.ai_display_tags = tags[:2]

        if user_styles and user_styles[0] in (shop.tags or ""):
            shop.ai_reason = f"Có style '{user_styles[0]}' đúng gu bạn"
        elif hasattr(shop, 'similarity'):
            shop.ai_reason = "Tương đồng cao với các quán bạn thích"
        else:
            shop.ai_reason = "Gợi ý khám phá mới"

    # TOP SECTION
    # service
    excluded_ids = [s.id for s in ai_shops]
    top_service_shops = CafeShop.objects.filter(
        rating__gte=4.0,
        avg_service__gte=0.8
    ).exclude(id__in=excluded_ids).order_by('-avg_service')[:5]
    excluded_ids.extend(s.id for s in top_service_shops)

    # ambiance
    top_ambiance_shops = CafeShop.objects.filter(
        rating__gte=4.0,
        avg_ambiance__gte=0.8
    ).exclude(id__in=excluded_ids).order_by('-avg_ambiance')[:5]
    excluded_ids.extend([s.id for s in top_ambiance_shops])

    # drink
    top_drink_shops = CafeShop.objects.filter(
        rating__gte=4.0,
        avg_drink__gte=0.8
    ).exclude(id__in=excluded_ids).order_by('-avg_drink')[:5]

    # Dữ liệu trả về
    user_prefs = {
        'district': favorite_district,
        'style': user_styles,
        'price_range': price_range_display
    }

    similar_shops = CafeShop.objects.filter(rating__gte=4.0).exclude(id__in=[s.id for s in ai_shops]).order_by('?')[:6]

    context = {
        'favorite_shops': favorite_shops,
        'ai_shops': ai_shops,
        'similar_shops': similar_shops,
        'top_service_shops': top_service_shops,
        'top_ambiance_shops': top_ambiance_shops,
        'top_drink_shops': top_drink_shops,
        'user_prefs': user_prefs,
    }
    return render(request, 'for_you.html', context)


def filtered_shops(request):
    shops = CafeShop.objects.all().order_by('-id')

    # search
    query = request.GET.get('search')
    if query:
        shops = shops.filter(
            Q(name__icontains=query) |
            Q(address__icontains=query) |
            Q(tags__icontains=query)
        )

    # filtered district
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
    context = {'shops': paginator.get_page(page_number),
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
    shop = get_object_or_404(
        CafeShop.objects.annotate(
            rating_avg=Avg('reviews__rating'),
            review_count=Count('reviews')
        ),
        pk=shop_id
    )

    # ====== Log lượt xem ======
    if request.user.is_authenticated:
        obj, created = ShopViewLog.objects.get_or_create(
            user=request.user,
            shop=shop
        )
        if not created:
            obj.view_count = F('view_count') + 1
            obj.save()

    # ====== MENU ======
    menu_items = shop.menu_items.all().order_by('category', 'id')
    grouped_menu = {}
    for item in menu_items:
        category = item.category or "Menu chung"
        grouped_menu.setdefault(category, [])
        price_formatted = f"{item.price:,.0f}₫".replace(",", "tmp").replace(".", ",").replace("tmp", ".")
        grouped_menu[category].append({
            'name': item.name,
            'price': price_formatted
        })

    reviews = shop.reviews.select_related('user').order_by('-created_at')

    related_shops = CafeShop.objects.filter(
        district=shop.district
    ).exclude(id=shop.id)[:4]

    is_saved = False
    if request.user.is_authenticated:
        is_saved = SavedShop.objects.filter(
            user=request.user,
            shop=shop
        ).exists()

    return render(request, 'shop_detail.html', {
        'shop': shop,
        'grouped_menu': grouped_menu,
        'reviews': reviews,
        'related_shops': related_shops,
        'is_saved': is_saved,
    })


# =============== AI ===============
@login_required
def submit_review(request, shop_id):
    if request.method == "POST":
        shop = get_object_or_404(CafeShop, id=shop_id)

        rating = int(request.POST.get("rating", 0))
        comment = request.POST.get("comment", "").strip()

        if rating == 0 or not comment:
            return JsonResponse({
                'success': False,
                'message': 'Vui lòng nhập đủ số sao và bình luận'
            })

        ai_scores = analyze_review_sentiment(comment)

        review, created = Review.objects.get_or_create(
            shop=shop,
            user=request.user,
            defaults={
                "rating": rating,
                "comment": comment,
                **ai_scores
            }
        )

        if not created:
            review.rating = rating
            review.comment = comment
            for k, v in ai_scores.items():
                setattr(review, k, v)
            review.save()

        update_shop_stats(shop)

        # rating chung
        shop.rating = Review.objects.filter(shop=shop).aggregate(
            avg=Avg("rating")
        )["avg"] or 0
        shop.save()

        return JsonResponse({
            'success': True,
            'review': {
                'username': request.user.username,
                'rating': review.rating,
                'comment': review.comment,
                'created_at': review.created_at.strftime("%d/%m/%Y") if hasattr(review,
                                                                                      'created_at') else "Vừa xong",
            },
            'message': 'Cảm ơn bạn đã đánh giá!'
        })

    return JsonResponse({'success': False, 'message': 'Yêu cầu không hợp lệ'})


def update_shop_stats(shop):
    aggs = shop.reviews.aggregate(
        avg_service=Avg('sentiment_service'),
        avg_ambiance=Avg('sentiment_ambiance'),
        avg_drink=Avg('sentiment_drink'),
        avg_price=Avg('sentiment_price')
    )

    shop.avg_service = aggs['avg_service'] or 0
    shop.avg_ambiance = aggs['avg_ambiance'] or 0
    shop.avg_drink = aggs['avg_drink'] or 0
    shop.avg_price = aggs['avg_price'] or 0
    shop.save()


def exclude_saved_shops(queryset, user):
    if user.is_authenticated:
        saved_ids = SavedShop.objects.filter(
            user=user
        ).values_list('shop_id', flat=True)
        return queryset.exclude(id__in=saved_ids)
    return queryset


# Luu quan
def toggle_save_shop(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    shop_id = request.POST.get("shop_id")
    shop = get_object_or_404(CafeShop, id=shop_id)

    # CHƯA LOGIN
    if not request.user.is_authenticated:
        return JsonResponse(
            {"require_login": True},
            status=401
        )

    saved = SavedShop.objects.filter(
        user=request.user,
        shop=shop
    )

    if saved.exists():
        saved.delete()
        return JsonResponse({"saved": False})
    else:
        SavedShop.objects.create(
            user=request.user,
            shop=shop
        )
        return JsonResponse({"saved": True})
