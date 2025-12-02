from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import CafeShop, MenuItem, ShopImage, Review, SavedShop, Contact

admin.site.register(CafeShop)
admin.site.register(MenuItem)
admin.site.register(ShopImage)
admin.site.register(Review)
admin.site.register(SavedShop)
admin.site.register(Contact)