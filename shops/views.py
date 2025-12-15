from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from .models import CafeShop, Contact, ShopViewLog, Review
from django.db.models import Avg, Count, F
from django.core.paginator import Paginator
from .ai_utils import analyze_review_sentiment, get_collaboration_recommendation
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

def for_you_view(request):
    return render(request, 'for_you.html')

def shop_list_view(request):
    shops = CafeShop.objects.all().order_by('-id')
    paginator = Paginator(shops, 8)
    page_number = request.GET.get('page')
    context = {
        'shops': paginator.get_page(page_number)
    }
    return render(request, 'shop_list.html', context)

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
    # 1. Query Shop & Annotate dữ liệu thống kê
    shop = get_object_or_404(
        CafeShop.objects.annotate(
            rating_avg=Avg('reviews__rating'),
            review_count=Count('reviews')
        ),
        pk=shop_id
    )

    # 2. GHI NHẬN LƯỢT XEM (Recommendation Data)
    if request.user.is_authenticated:
        obj, created = ShopViewLog.objects.get_or_create(
            user=request.user,
            shop=shop
        )
        if not created:
            # Dùng F() expression để tránh race condition
            obj.view_count = F('view_count') + 1
            obj.save()

    # 3. Xử lý Menu
    menu_items = shop.menu_items.all().order_by('category', 'id')
    grouped_menu = {}
    for item in menu_items:
        category = item.category if item.category else "Menu chung"
        if category not in grouped_menu:
            grouped_menu[category] = []

        # Format giá tiền
        price_formatted = f"{item.price:,.0f}₫".replace(",", "tmp").replace(".", ",").replace("tmp", ".")
        grouped_menu[category].append({'name': item.name, 'price': price_formatted})

    # 4. Lấy reviews
    reviews = shop.reviews.all().select_related('user').order_by('-created_at')

    # 5. Lấy quán liên quan (cùng quận)
    related_shops = CafeShop.objects.filter(district=shop.district).exclude(pk=shop_id)[:3]

    context = {
        'shop': shop,
        'grouped_menu': grouped_menu,
        'reviews': reviews,
        'related_shops': related_shops,
    }
    return render(request, 'shop_detail.html', context)

# =============== AI ===============
@login_required(login_url='/login/')
def submit_review(request, shop_id):
    shop = get_object_or_404(CafeShop, pk=shop_id)
    if request.method == 'POST':
        comment_text = request.POST.get('comment', '').strip()
        rating_value = request.POST.get('rating')

        if not rating_value or not comment_text:
            messages.error(request, "Vui lòng nhập nội dung và chọn số sao!")
            return redirect('shop_detail', shop_id=shop_id)

        ai_scores = analyze_review_sentiment(comment_text)
        try:
            Review.objects.create(
                shop=shop,
                user=request.user,
                comment=comment_text,
                rating=int(rating_value),
                **ai_scores
            )
            messages.success(request, "Cảm ơn bạn đã đánh giá!")
            update_shop_stats(shop)
        except Exception as e:
            print(e)
            messages.error(request, "Có lỗi xảy ra, vui lòng thử lại.")

    return redirect('shop_detail', shop_id=shop_id)

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