from django.shortcuts import render, get_object_or_404, redirect
from .models import CafeShop, Contact, ShopViewLog
from django.db.models import Avg, Count, F
from django.core.paginator import Paginator
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