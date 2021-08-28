from . import models
from django.urls import reverse
from django.contrib import admin, messages
from django.db.models.aggregates import Count
from django.utils.html import format_html, urlencode


class InventoryFilter(admin.SimpleListFilter):
    title = "inventory"
    parameter_name = "inventory"

    def lookups(self, request, model_admin):
        return [("<10", "Low")]

    def queryset(self, request, queryset):
        if self.value() == "<10":
            return queryset.filter(inventory__lt=10)


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    search_fields = ["title"]
    actions = ["clear_inventory"]
    list_editable = ["unit_price"]
    list_select_related = ["collection"]
    autocomplete_fields = ["collection"]
    prepopulated_fields = {"slug": ["title"]}
    list_filter = ["collection", "last_update", InventoryFilter]
    list_display = ["title", "unit_price", "inventory_status", "collection_title"]

    # related object so decrease queries by addin select_related
    def collection_title(self, product):
        return product.collection.title

    @admin.display(ordering="inventory")
    def inventory_status(self, product):
        if product.inventory < 10:
            return "Low"

        return "Okay"

    @admin.action(description="Clear inventory")
    def clear_inventory(self, request, queryset):
        updated_count = queryset.update(inventory=0)
        self.message_user(
            request,
            f"{updated_count} products were successfully updated",
            messages.SUCCESS,
        )


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_editable = ["membership"]
    ordering = ["first_name", "last_name"]
    search_fields = ["first_name__istartswith", "last_name__istartswith"]
    list_display = ["first_name", "last_name", "membership", "orders_list"]

    @admin.display(ordering="orders_list")
    def orders_list(self, customer):
        url = (
            reverse("admin:store_order_changelist")
            + "?"
            + urlencode({"customer__id": str(customer.id)})
        )

        return format_html(f"<a  href='{url}'>{customer.orders_list}</a>")

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(orders_list=Count("order"))


class OrderItemInline(admin.TabularInline):
    extra = 0
    min_num = 1
    max_num = 10
    model = models.OrderItem
    autocomplete_fields = ["product"]


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_per_page = 10
    inlines = [OrderItemInline]
    ordering = ["payment_status"]
    list_select_related = ["customer"]
    autocomplete_fields = ["customer"]
    list_display = ["id", "customer", "placed_at", "payment_status"]

    def customer_name(self, order):
        return f"{order.customer.first_name} {order.customer.last_name}"


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    search_fields = ["title"]
    list_display = ["title", "products_count"]

    @admin.display(ordering="products_count")
    def products_count(self, collection):
        url = (
            reverse("admin:store_product_changelist")
            + "?"
            + urlencode({"collection__id": str(collection.id)})
        )

        return format_html(f"<a href='{url}'> {collection.products_count} </a>")

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(products_count=Count("product"))
