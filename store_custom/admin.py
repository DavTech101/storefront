from store.models import Product
from django.contrib import admin
from tags.models import TaggedItem
from store.admin import ProductAdmin
from django.contrib.contenttypes.admin import GenericTabularInline

# Register your models here.
class TagInline(GenericTabularInline):
    extra = 0
    model = TaggedItem
    autocomplete_fields = ["tag"]


class CustomProductAdmin(ProductAdmin):
    inlines = [TagInline]


admin.site.unregister(Product)
admin.site.register(Product, CustomProductAdmin)
