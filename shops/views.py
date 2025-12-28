from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.http import JsonResponse
from django.contrib import messages
from .models import CafeShop, Contact, ShopViewLog, Review
from django.db.models import Avg, Count, F
from django.core.paginator import Paginator
from .models import SavedShop
from .ai_utils import analyze_review_sentiment, get_collaboration_recommendation
# Create your views here.
from django.db.models import Count

def home_view(request):
    hot_shop = CafeShop.objects.order_by(
        '-rating',
        '-avg_service_score',
        '-avg_drink_score'
    )

    new_shop = CafeShop.objects.order_by('-id')
    popular_shop = CafeShop.objects.annotate(
        view_total=Count('shopviewlog')
    ).order_by('-view_total')

    hot_shop = exclude_saved_shops(hot_shop, request.user)
    new_shop = exclude_saved_shops(new_shop, request.user)
    popular_shop = exclude_saved_shops(popular_shop, request.user)

    return render(request, 'home.html', {
        'hot_shop': hot_shop[:6],
        'new_shop': new_shop[:6],
        'popular_shop': popular_shop[:6],
    })


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
    context = { 'shops': paginator.get_page(page_number),
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
    shop = get_object_or_404(CafeShop, id=shop_id)

    if request.method == "POST":
        rating = int(request.POST.get("rating", 0))
        comment = request.POST.get("comment", "").strip()

        if rating == 0 or not comment:
            messages.error(request, "Vui lòng nhập đánh giá và nội dung.")
            return redirect("shop_detail", shop.id)

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

        messages.success(request, "Cảm ơn bạn đã đánh giá!")

    return redirect("shop_detail", shop.id)



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

@login_required
def for_you_view(request):
    user = request.user
    saved_ids = SavedShop.objects.filter(
        user=user
    ).values_list('shop_id', flat=True)

    favorite_shops = CafeShop.objects.filter(
        id__in=saved_ids
    )

    recommended_shops = [
        shop for shop in get_collaboration_recommendation(user)
        if shop.id not in saved_ids
    ][:6]

    trending_shops = CafeShop.objects.annotate(
        view_total=Count('shopviewlog')
    ).exclude(
        id__in=saved_ids
    ).order_by('-view_total')[:6]

    return render(request, "for_you.html", {
        "favorite_shops": favorite_shops,
        "recommended_shops": recommended_shops,
        "trending_shops": trending_shops,
    })
