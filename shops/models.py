from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
import requests

def normalize_comma_separated_string(value):
    if not value:
        return ""

    cleaned_value = value.strip()
    item_list = [item.strip() for item in cleaned_value.split(',') if item.strip()]
    return ','.join(item_list)

#Model chính cho quán Cafe
DISTRICT_CHOICES = [
    ('Quận 1', 'Quận 1'),
    ('Quận 2', 'Quận 2'),
    ('Quận 3', 'Quận 3'),
    ('Quận 4', 'Quận 4'),
    ('Quận 5', 'Quận 5'),
    ('Quận 6', 'Quận 6'),
    ('Quận 7', 'Quận 7'),
    ('Quận 8', 'Quận 8'),
    ('Quận 9', 'Quận 9'),
    ('Quận 10', 'Quận 10'),
    ('Quận 11', 'Quận 11'),
    ('Quận 12', 'Quận 12'),
    ('Bình Tân', 'Quận Bình Tân'),
    ('Phú Nhuận', 'Quận Phú Nhuận'),
    ('Tân Bình', 'Quận Tân Bình'),
    ('Tân Phú', 'Quận Tân Phú'),
    ('Gò Vấp', 'Quận Gò Vấp'),
    ('Thủ Đức', 'TP. Thủ Đức'),
    ('Bình Thạnh', 'Bình Thạnh'),
]

TAG_CHOICES = [
    ('Hiện đại', 'Hiện đại'),
    ('Ấm cúng', 'Ấm cúng'),
    ('Yên tĩnh', 'Yên tĩnh'),
    ('Sang trọng', 'Sang trọng'),
    ('Hoài cổ', 'Hoài cổ'),
    ('Nghệ thuật', 'Nghệ thuật'),
]

AMENITY_CHOICES = [
    ('Wifi', 'Wifi'),
    ('Điều hòa', 'Điều hòa'),
    ('Ổ cắm điện', 'Ổ cắm điện'),
    ('Chỗ đậu xe', 'Chỗ đậu xe'),
    ('View đẹp', 'View đẹp'),
    ('Sân vườn', 'Sân vườn'),
]

PRICE_CHOICES = [
    ('Dưới 50.000đ', 'Dưới - 50.000đ'),
    ('50.000đ - 80.000đ', '50.000đ - 80.000đ'),
    ('Trên 80.000đ', 'Trên 80.000đ'),
]

class CafeShop(models.Model):
    name = models.CharField(max_length = 200)
    address = models.CharField(max_length = 300)
    district = models.CharField(max_length=100, choices=DISTRICT_CHOICES)

    tags = models.CharField(max_length = 300, blank = True)
    amenities = models.CharField(max_length = 300, blank = True) #Tiện ích các thứ như Wifi, Chỗ đậu xe...
    description = models.CharField(max_length = 300, blank = True) #Tối đa 20 chữ

    price_range = models.CharField(max_length=100, choices=PRICE_CHOICES, blank=True)
    cover_image = models.ImageField(upload_to = 'covers/', blank = True, null = True)
    rating = models.FloatField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(5)])

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    # RECOMMENDATION SYSTEM
    avg_service = models.FloatField(default = 0)
    avg_ambiance = models.FloatField(default = 0)
    avg_drink = models.FloatField(default = 0)
    avg_price = models.FloatField(default = 0)

    def save(self, *args, **kwargs):
        self.tags = normalize_comma_separated_string(self.tags)
        self.amenities = normalize_comma_separated_string(self.amenities)
        self.description = normalize_comma_separated_string(self.description)

        if self.address and (self.latitude is None or self.longitude is None):
            self.geocode_address()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_tag_list(self):
        if self.tags:
            return self.tags.split(',')
        return []

    def get_amenities_list(self):
        if self.amenities:
            return self.amenities.split(',')
        return []

    def get_min_price(self):
        try:
            return int(self.price_range.split('-')[0].replace('₫','').replace('.','').strip())
        except:
            return None

    def get_max_price(self):
        try:
            return int(self.price_range.split('-')[1].replace('₫','').replace('.','').strip())
        except:
            return None

    def geocode_address(self):
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": self.address,
            "key": settings.GOOGLE_MAPS_API_KEY
        }
        try:
            res = requests.get(url, params=params).json()
            if res["status"] == "OK":
                location = res["results"][0]["geometry"]["location"]
                self.latitude = location["lat"]
                self.longitude = location["lng"]
        except Exception as e:
            print(f"Error geocoding: {e}")

#Model cho Menu
class MenuItem(models.Model):
    shop = models.ForeignKey(CafeShop, on_delete = models.CASCADE, related_name = 'menu_items')
    category = models.CharField(max_length = 100)
    name = models.CharField(max_length = 100)
    description = models.CharField(max_length = 200, blank = True)
    price = models.IntegerField()

    def __str__(self):
        return f'{ self.name } ({self.shop.name})'

#Model cho Ảnh của quán
class ShopImage(models.Model):
    shop = models.ForeignKey(CafeShop, on_delete = models.CASCADE, related_name = 'images')
    image = models.ImageField(upload_to = 'shop_gallery/')

    def __str__(self):
        return f'Ảnh cho ({self.shop.name})'

#Model cho Đánh giá - Bình luận
class Review(models.Model):
    shop = models.ForeignKey(CafeShop, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(default=1)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    sentiment_service = models.IntegerField(default=0)
    sentiment_ambiance = models.IntegerField(default=0)
    sentiment_drink = models.IntegerField(default=0)
    sentiment_price = models.IntegerField(default=0)

    def __str__(self):
        return f'Review {self.shop.name} bởi {self.user.username}'

#Model cho nút lưu vào yêu thích
class SavedShop(models.Model):
    shop = models.ForeignKey(CafeShop, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('shop', 'user')

    def __str__(self):
        return f'{self.user} đã lưu {self.shop.name}'

#Model cho Liên hệ
class Contact (models.Model):
    fullname = models.CharField(max_length = 100)
    email = models.CharField(max_length = 100)
    topic = models.CharField(max_length = 100)
    content = models.TextField()

# Recommendation System
class ShopViewLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    shop = models.ForeignKey(CafeShop, on_delete=models.CASCADE)
    view_count = models.IntegerField(default=1)
    last_viewed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('shop', 'user')