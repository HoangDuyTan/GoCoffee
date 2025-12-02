from django.db import models
from django.contrib.auth.models import User

def normalize_comma_separated_string(value):
    if not value:
        return ""

    cleaned_value = value.strip()
    item_list = [item.strip() for item in cleaned_value.split(',') if item.strip()]
    return ','.join(item_list)

#Model chính cho quán Cafe
class CafeShop(models.Model):
    name = models.CharField(max_length = 200)
    address = models.CharField(max_length = 300)
    district = models.CharField(max_length = 100) #Dùng để lọc

    tags = models.CharField(max_length = 300, blank = True)
    amenities = models.CharField(max_length = 300, blank = True) #Tiện ích các thứ như Wifi, Chỗ đậu xe...
    description = models.CharField(max_length = 300, blank = True) #Tối đa 20 chữ

    price_range = models.CharField(max_length = 100, blank = True)
    cover_image = models.ImageField(upload_to = 'covers/', blank = True, null = True)

    def save(self, *args, **kwargs):
        self.tags = normalize_comma_separated_string(self.tags)
        self.amenities = normalize_comma_separated_string(self.amenities)
        self.description = normalize_comma_separated_string(self.description)
        super().save(*args, **kwargs)

    def get_tag_list(self):
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []

    def get_amenities_list(self):
        if self.amenities:
            return [amenity.strip() for amenity in self.amenities.split(',') if amenity.strip()]
        return []

    def __str__(self):
        return self.name


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
    shop = models.ForeignKey(CafeShop, on_delete = models.CASCADE, related_name = 'reviews')
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    rating = models.IntegerField(default = 1)
    comment = models.TextField(blank = True)
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f'Review {self.shop.name} bởi {self.user.username}'

#Model cho nút lưu vào yêu thích
class SavedShop(models.Model):
    shop = models.ForeignKey(CafeShop, on_delete = models.CASCADE)
    user = models.ForeignKey(User, on_delete = models.CASCADE)

    class Meta:
        unique_together = ('shop', 'user') #Đảm bảo 1 user không thể lưu 1 quán 2 lần

    def __str__(self):
        return f'{self.user.username} đã lưu {self.shop.name}'

#Model cho Liên hệ
class Contact (models.Model):
    fullname = models.CharField(max_length = 100)
    email = models.CharField(max_length = 100)
    topic = models.CharField(max_length = 100)
    content = models.TextField()