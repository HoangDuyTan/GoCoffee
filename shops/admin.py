from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django import forms
from .models import CafeShop, MenuItem, ShopImage, Review, SavedShop, Contact
from .models import TAG_CHOICES, AMENITY_CHOICES


class CafeShopAdminForm(forms.ModelForm):
    tags = forms.MultipleChoiceField(
        choices=TAG_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    amenities = forms.MultipleChoiceField(
        choices=AMENITY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = CafeShop
        fields = '__all__'

    def clean_tags(self):
        data = self.cleaned_data['tags']
        return ','.join(data)

    def clean_amenities(self):
        data = self.cleaned_data['amenities']
        return ','.join(data)

    def __init__(self, *args, **kwargs):
        super(CafeShopAdminForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            if self.instance.tags:
                self.fields['tags'].initial = self.instance.tags.split(',')
            if self.instance.amenities:
                self.fields['amenities'].initial = self.instance.amenities.split(',')

class CafeShopAdmin(admin.ModelAdmin):
    form = CafeShopAdminForm
    list_display = ('name', 'district', 'price_range', 'rating', 'view_count_display')
    search_fields = ('name', 'district')
    list_filter = ('district', 'price_range')

    def view_count_display(self, obj):
        return obj.shopviewlog_set.count()

    view_count_display.short_description = "Lượt xem"

admin.site.register(CafeShop, CafeShopAdmin)
admin.site.register(MenuItem)
admin.site.register(ShopImage)
admin.site.register(Review)
admin.site.register(SavedShop)
admin.site.register(Contact)