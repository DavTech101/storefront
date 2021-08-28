from tags.models import TaggedItem
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models.functions import Concat
from django.db import transaction, connection
from django.db.models.fields import DecimalField
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, F, Value, Func, ExpressionWrapper
from django.db.models.aggregates import Count, Max, Min, Avg, Sum
from store.models import Customer, Product, OrderItem, Order, Collection


# @transaction.atomic() -> Transaction to prevent data loss
def say_hello(request):
    # query_set = Product.objects.filter(pk=0).first()  # also checks for empty
    # query_set = Product.objects.filter(
    #     Q(inventory__lt=10) | Q(unit_price__lt=20))

    # query_set = Product.objects.filter(inventory=F('unit_price'))

    # query_set = Product.objects.order_by('title') -> Ascending

    # # query_set = Product.objects.order_by('-title') -> Descending

    # query_set = Product.objects.values(
    #     'title', 'orderitem__product_id').order_by('title')

    # query_set = Product.objects.filter(
    #     id__in=OrderItem.objects.values('product_id').distinct()).order_by('title')

    # select_related -> relation is (1)
    # prefetch_related -> relation is (n) -> ManyToMany
    # query_set = Product.objects.select_related('collection').all()
    # query_set = Product.objects.prefetch_related('promotions').all()
    # query_set = Product.objects.prefetch_related(
    #     'promotions').select_related('collection').all()

    query_set = Order.objects.select_related(
        'customer').prefetch_related('orderitem_set__product ').order_by('-placed_at')[:5]

    results = Product.objects.filter(collection_id=1).aggregate(count=Count(
        'id'), min_price=Min('unit_price'), max_price=Max('unit_price'), avg_price=Avg('unit_price'), sum_price=Sum('unit_price'))

    # return_set = Customer.objects.annotate(new_id=F('id'))

    # return_set = Customer.objects.annotate(full_name=Func(
    #     F('first_name'), F('last_name'), function='CONCAT')
    # )
    # return_set = Customer.objects.annotate(
    #     full_name=Concat('first_name', Value(' '), 'last_name'))

    # return_set = Customer.objects.annotate(orders_count=Count('order '))

    # discounted_price = ExpressionWrapper(
    #     F('unit_price')*0.8, output_field=DecimalField())
    # return_set = Product.objects.annotate(
    #     discounted_price=discounted_price
    # )

    # Created a costumed manager for the below
    # content_type = ContentType.objects.get_for_model(Product)
    # return_set = TaggedItem.objects \
    #     .select_related('tag') \
    #     .filter(
    #         content_type=content_type,
    #         object_id=1
    #     )

    return_set = TaggedItem.objects.get_tags_for(Product, 1)

    # Updating fields
    # collection = Collection.objects.get(pk=11)
    # collection.title = 'Video Games'
    # collection.featured_product = None
    # collection.save()

    # Updating field second way
    # Collection.objects.filter(pk=11).update(featured_product=None)

    # Delete single and many entries
    # collection = Collection(pk=11)
    # collection.delete()

    # Collection.objects.filter(id__gt=5).delete()

    # Transaction to prevent data losss
    # with transaction.atomic():
    #     order = Order()
    #     order.customer_id = 1
    #     order.save()

    #     item = OrderItem()
    #     item.order = order
    #     item.product_id = 1
    #     item.quantity = 1
    #     item.unit_price = 10
    #     item.save()

    # Executing Raw SQL queries
    # Product.objects.raw('SELECT * FROM store_product')

    # Executing Raw SQL queries with django package -> Closes automatically
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM store_product')
        # Look into this for easier look up vvv
        cursor.callproc('get_customers', [1, 2, 3, 4])

    return render(request, 'hello.html', {'name': 'Mosh', 'products': list(query_set), 'result': results, 'returnedset': list(return_set)})
