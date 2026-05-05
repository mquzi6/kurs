from django.db import models
from django.conf import settings
from django.utils import timezone
from .utils import generate_order_number

class Cart(models.Model):
    """Корзина покупок"""
    session_key = models.CharField(max_length=40, verbose_name='Сессия')
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Пользователь')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
    
    def __str__(self):
        return f"Корзина {self.session_key}"
    
    def get_total_price(self):
        """Возвращает общую стоимость товаров в корзине"""
        return sum(item.get_total_price() for item in self.items.all())
    
    def get_item_count(self):
        """Возвращает общее количество товаров в корзине"""
        return sum(item.quantity for item in self.items.all())

class CartItem(models.Model):
    """Элемент корзины"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name='Корзина')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, verbose_name='Товар')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    
    class Meta:
        verbose_name = 'Элемент корзины'
        verbose_name_plural = 'Элементы корзины'
        unique_together = ['cart', 'product']
    
    def __str__(self):
        return f"{self.product.title} x {self.quantity}"
    
    def get_total_price(self):
        """Возвращает общую стоимость позиции"""
        return self.product.price * self.quantity

class Order(models.Model):
    """Заказ"""
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
        ('refunded', 'Возвращен'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('paid', 'Оплачен'),
        ('failed', 'Оплата не удалась'),
        ('refunded', 'Возвращен'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('card', 'Банковская карта'),
        ('cash', 'Наличные'),
        ('online', 'Онлайн платеж'),
    ]
    
    DELIVERY_METHOD_CHOICES = [
        ('pickup', 'Самовывоз'),
        ('courier', 'Курьер'),
        ('post', 'Почта'),
        ('digital', 'Электронная доставка'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Пользователь')
    order_number = models.CharField(max_length=20, unique=True, editable=False, verbose_name='Номер заказа')
    
    # Информация о доставке
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    
    delivery_address = models.TextField(blank=True, verbose_name='Адрес доставки')
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_METHOD_CHOICES, default='pickup', verbose_name='Способ доставки')
    
    # Информация об оплате
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='card', verbose_name='Способ оплаты')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending', verbose_name='Статус оплаты')
    
    # Статус заказа
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус заказа')
    
    # Цены
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Промежуточная сумма')
    delivery_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Стоимость доставки')
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Скидка')
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Итого')
    
    # Дополнительная информация
    notes = models.TextField(blank=True, verbose_name='Заметки')
    tracking_number = models.CharField(max_length=100, blank=True, verbose_name='Трекинг номер')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата оплаты')
    shipped_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата отправки')
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата доставки')
    
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Заказ {self.order_number}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = generate_order_number()
        super().save(*args, **kwargs)
    
    def get_total_items(self):
        """Возвращает общее количество товаров в заказе"""
        return sum(item.quantity for item in self.items.all())
    
    def mark_as_paid(self):
        """Отмечает заказ как оплаченный"""
        self.payment_status = 'paid'
        self.paid_at = timezone.now()
        self.save()
    
    def mark_as_shipped(self):
        """Отмечает заказ как отправленный"""
        self.status = 'shipped'
        self.shipped_at = timezone.now()
        self.save()
    
    def mark_as_delivered(self):
        """Отмечает заказ как доставленный"""
        self.status = 'delivered'
        self.delivered_at = timezone.now()
        self.save()

class OrderItem(models.Model):
    """Элемент заказа"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Заказ')
    product = models.ForeignKey('products.Product', on_delete=models.SET_NULL, null=True, verbose_name='Товар')
    title = models.CharField(max_length=255, verbose_name='Название')  # Сохраняем название на случай удаления товара
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма')
    
    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'
    
    def __str__(self):
        return f"{self.title} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        self.total = self.price * self.quantity
        super().save(*args, **kwargs)

class Wishlist(models.Model):
    """Список желаний"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, verbose_name='Товар')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    
    class Meta:
        verbose_name = 'Список желаний'
        verbose_name_plural = 'Списки желаний'
        unique_together = ['user', 'product']
    
    def __str__(self):
        return f"{self.user.username} - {self.product.title}"

class Review(models.Model):
    """Отзывы о товарах"""
    RATING_CHOICES = [(i, f'{i} звезда') for i in range(1, 6)]
    
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='reviews', verbose_name='Товар')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, verbose_name='Оценка')
    title = models.CharField(max_length=200, blank=True, verbose_name='Заголовок')
    comment = models.TextField(verbose_name='Комментарий')
    is_approved = models.BooleanField(default=False, verbose_name='Одобрен')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Отзыв на {self.product.title} от {self.user.username}"