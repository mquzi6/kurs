from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name

class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Старая цена')
    stock = models.PositiveIntegerField(default=0, verbose_name='Количество на складе')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Категория')
    image = models.ImageField(upload_to='products/', null=True, blank=True, verbose_name='Изображение')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    is_digital = models.BooleanField(default=False, verbose_name='Цифровой товар')
    digital_file = models.FileField(upload_to='digital_products/', null=True, blank=True, verbose_name='Файл товара')
    sku = models.CharField(max_length=100, unique=True, null=True, blank=True, verbose_name='Артикул')
    brand = models.CharField(max_length=100, blank=True, verbose_name='Бренд')
    specifications = models.JSONField(default=dict, blank=True, null=True, verbose_name='Характеристики')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']

    def __str__(self):
        return self.title
    
    def get_price(self):
        """Возвращает актуальную цену (со скидкой если есть)"""
        return self.price if not self.old_price or self.price < self.old_price else self.price
    
    def has_discount(self):
        """Проверяет есть ли скидка"""
        return self.old_price and self.price < self.old_price
    
    def get_discount_percentage(self):
        """Возвращает процент скидки"""
        if self.has_discount():
            return int((1 - self.price / self.old_price) * 100)
        return 0

class ProductImage(models.Model):
    """Дополнительные изображения товара"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name='Товар')
    image = models.ImageField(upload_to='products/', verbose_name='Изображение')
    is_main = models.BooleanField(default=False, verbose_name='Главное изображение')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Изображение товара'
        verbose_name_plural = 'Изображения товаров'
    
    def __str__(self):
        return f"Изображение для {self.product.title}"
