import random
import string
from datetime import datetime


def generate_order_number():
    """
    Генерирует уникальный номер заказа в формате:
    ORD-YYYYMMDD-XXXX, где XXXX - случайные символы
    """
    date_str = datetime.now().strftime('%Y%m%d')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f'ORD-{date_str}-{random_str}'


def get_or_create_cart(request):
    """
    Получает или создает корзину для текущего пользователя/сессии
    """
    from .models import Cart
    
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        cart, created = Cart.objects.get_or_create(session_key=session_key)
        
        # Если пользователь вошел в систему, привязываем корзину к его аккаунту
        if request.user.is_authenticated:
            cart.user = request.user
            cart.save()
    
    return cart


def calculate_shipping_price(delivery_method, total_amount=0):
    """
    Рассчитывает стоимость доставки в зависимости от способа и суммы заказа
    """
    shipping_prices = {
        'pickup': 0,  # Самовывоз бесплатно
        'courier': 300,  # Курьер
        'post': 200,  # Почта
        'digital': 0,  # Электронная доставка бесплатно
    }
    
    base_price = shipping_prices.get(delivery_method, 0)
    
    # Бесплатная доставка при заказе от 5000 рублей
    if total_amount >= 5000 and delivery_method in ['courier', 'post']:
        return 0
    
    return base_price