from django.shortcuts import render, get_object_or_404
from .models import CafeShop

# Create your views here.
def home_view(request):
    new_shop = CafeShop.objects.all().order_by('-id')[:3]
    hot_shop = CafeShop.objects.all()[:3]
    context = {
        'new_shop': new_shop,
        'hot_shop': hot_shop
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