import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kurs.settings')
django.setup()

from products.models import Product, Category
from users.models import Cart, Order

print("Models loaded successfully!")
print(f"Categories: {Category.objects.count()}")
print(f"Products: {Product.objects.count()}")
print(f"Carts: {Cart.objects.count()}")
print(f"Orders: {Order.objects.count()}")