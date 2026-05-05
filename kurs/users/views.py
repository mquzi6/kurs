from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, DetailView
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.db.models import Sum
from .models import Cart, CartItem, Order, OrderItem, Wishlist, Review
from .utils import get_or_create_cart, calculate_shipping_price
from products.models import Product
import json


class CartView(View):
    """Представление корзины"""
    
    def get(self, request):
        cart = get_or_create_cart(request)
        cart_items = cart.items.select_related('product').all()
        total_price = cart.get_total_price()
        item_count = cart.get_item_count()
        
        context = {
            'cart': cart,
            'cart_items': cart_items,
            'total_price': total_price,
            'item_count': item_count,
        }
        return render(request, 'users/cart.html', context)


@method_decorator(require_POST, name='dispatch')
class CartAddView(View):
    """Добавление товара в корзину"""
    
    def post(self, request):
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        if not product_id:
            messages.error(request, 'Товар не выбран')
            return redirect('product-list')
        
        product = get_object_or_404(Product, id=product_id, is_active=True)
        
        # Проверяем наличие
        if product.stock < quantity:
            messages.error(request, f'Недостаточно товара на складе. Доступно: {product.stock}')
            return redirect('product-list')
        
        cart = get_or_create_cart(request)
        
        # Проверяем, есть ли уже такой товар в корзине
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            # Если товар уже есть, увеличиваем количество
            new_quantity = cart_item.quantity + quantity
            if new_quantity > product.stock:
                messages.error(request, f'Недостаточно товара на складе. Доступно: {product.stock}')
            else:
                cart_item.quantity = new_quantity
                cart_item.save()
                messages.success(request, f'Товар "{product.title}" добавлен в корзину')
        else:
            messages.success(request, f'Товар "{product.title}" добавлен в корзину')
        
        # Если это AJAX запрос, возвращаем JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'item_count': cart.get_item_count(),
                'total_price': str(cart.get_total_price())
            })
        
        return redirect('cart')


@method_decorator(require_POST, name='dispatch')
class CartUpdateView(View):
    """Обновление количества товара в корзине"""
    
    def post(self, request, item_id):
        cart_item = get_object_or_404(CartItem, id=item_id)
        action = request.POST.get('action')
        
        if action == 'increase':
            if cart_item.product.stock > cart_item.quantity:
                cart_item.quantity += 1
                cart_item.save()
                messages.success(request, 'Количество товара увеличено')
            else:
                messages.error(request, 'Недостаточно товара на складе')
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
                messages.success(request, 'Количество товара уменьшено')
            else:
                messages.info(request, 'Для удаления товара используйте кнопку "Удалить"')
        
        # Если это AJAX запрос, возвращаем JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            cart = cart_item.cart
            return JsonResponse({
                'success': True,
                'item_count': cart.get_item_count(),
                'total_price': str(cart.get_total_price()),
                'item_total': str(cart_item.get_total_price())
            })
        
        return redirect('cart')


@method_decorator(require_POST, name='dispatch')
class CartRemoveView(View):
    """Удаление товара из корзины"""
    
    def post(self, request, item_id):
        cart_item = get_object_or_404(CartItem, id=item_id)
        product_title = cart_item.product.title
        cart_item.delete()
        messages.success(request, f'Товар "{product_title}" удален из корзины')
        
        # Если это AJAX запрос, возвращаем JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            cart = cart_item.cart
            return JsonResponse({
                'success': True,
                'item_count': cart.get_item_count(),
                'total_price': str(cart.get_total_price())
            })
        
        return redirect('cart')


class CheckoutView(View):
    """Оформление заказа"""
    
    def get(self, request):
        cart = get_or_create_cart(request)
        
        if not cart.items.exists():
            messages.warning(request, 'Ваша корзина пуста')
            return redirect('cart')
        
        # Получаем данные пользователя, если он авторизован
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
            }
        
        context = {
            'cart': cart,
            'cart_items': cart.items.select_related('product').all(),
            'total_price': cart.get_total_price(),
            'shipping_options': [
                ('pickup', 'Самовывоз', 0),
                ('courier', 'Курьер', 300),
                ('post', 'Почта', 200),
                ('digital', 'Электронная доставка', 0),
            ],
            'payment_options': [
                ('card', 'Банковская карта'),
                ('cash', 'Наличные'),
                ('online', 'Онлайн платеж'),
            ],
        }
        return render(request, 'users/checkout.html', context)
    
    def post(self, request):
        cart = get_or_create_cart(request)
        
        if not cart.items.exists():
            messages.error(request, 'Ваша корзина пуста')
            return redirect('cart')
        
        # Получаем данные из формы
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        delivery_address = request.POST.get('delivery_address', '')
        delivery_method = request.POST.get('delivery_method', 'pickup')
        payment_method = request.POST.get('payment_method', 'card')
        notes = request.POST.get('notes', '')
        
        # Создаем заказ
        subtotal = cart.get_total_price()
        delivery_price = calculate_shipping_price(delivery_method, subtotal)
        discount = 0  # Можно добавить логику скидок
        total = subtotal + delivery_price - discount
        
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            delivery_address=delivery_address,
            delivery_method=delivery_method,
            payment_method=payment_method,
            subtotal=subtotal,
            delivery_price=delivery_price,
            discount=discount,
            total=total,
            notes=notes,
        )
        
        # Переносим товары из корзины в заказ
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                title=cart_item.product.title,
                price=cart_item.product.price,
                quantity=cart_item.quantity,
                total=cart_item.get_total_price()
            )
            
            # Уменьшаем количество товара на складе
            cart_item.product.stock -= cart_item.quantity
            cart_item.product.save()
        
        # Очищаем корзину
        cart.items.all().delete()
        
        messages.success(request, f'Заказ {order.order_number} успешно оформлен!')
        return redirect('order_detail', order_number=order.order_number)


class OrderDetailView(DetailView):
    """Детали заказа"""
    model = Order
    template_name = 'users/order_detail.html'
    context_object_name = 'order'
    slug_field = 'order_number'
    slug_url_kwarg = 'order_number'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Показываем только заказы текущего пользователя или неавторизованным по session
        if self.request.user.is_authenticated:
            queryset = queryset.filter(user=self.request.user)
        return queryset


class OrderHistoryView(View):
    """История заказов"""
    
    def get(self, request):
        if not request.user.is_authenticated:
            messages.warning(request, 'Пожалуйста, войдите в систему')
            return redirect('login')
        
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        context = {'orders': orders}
        return render(request, 'users/order_history.html', context)


class WishlistView(View):
    """Список желаний"""
    
    def get(self, request):
        if not request.user.is_authenticated:
            messages.warning(request, 'Пожалуйста, войдите в систему')
            return redirect('login')
        
        wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
        context = {'wishlist_items': wishlist_items}
        return render(request, 'users/wishlist.html', context)
    
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'Необходимо войти в систему'})
        
        product_id = request.POST.get('product_id')
        if not product_id:
            return JsonResponse({'success': False, 'message': 'Товар не выбран'})
        
        product = get_object_or_404(Product, id=product_id, is_active=True)
        
        # Проверяем, есть ли уже в списке желаний
        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product
        )
        
        if created:
            return JsonResponse({'success': True, 'message': 'Товар добавлен в список желаний'})
        else:
            return JsonResponse({'success': False, 'message': 'Товар уже в списке желаний'})


@method_decorator(require_POST, name='dispatch')
class WishlistRemoveView(View):
    """Удаление из списка желаний"""
    
    def post(self, request, product_id):
        if not request.user.is_authenticated:
            messages.error(request, 'Необходимо войти в систему')
            return redirect('login')
        
        wishlist_item = get_object_or_404(Wishlist, user=request.user, product_id=product_id)
        wishlist_item.delete()
        messages.success(request, 'Товар удален из списка желаний')
        return redirect('wishlist')


class SignupView(View):
    """Регистрация нового пользователя"""
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('product-list')
        form = UserCreationForm()
        return render(request, 'users/signup.html', {'form': form})
    
    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('product-list')
        return render(request, 'users/signup.html', {'form': form})

class LogoutView(View):
    """Выход из системы"""
    
    def get(self, request):
        logout(request)
        messages.success(request, 'Вы успешно вышли из системы')
        return redirect('product-list')

class ReviewCreateView(View):
    """Создание отзыва"""
    
    def post(self, request, product_id):
        if not request.user.is_authenticated:
            messages.error(request, 'Необходимо войти в систему')
            return redirect('login')
        
        product = get_object_or_404(Product, id=product_id, is_active=True)
        
        # Проверяем, не оставлял ли пользователь уже отзыв
        existing_review = Review.objects.filter(user=request.user, product=product).first()
        if existing_review:
            messages.error(request, 'Вы уже оставляли отзыв на этот товар')
            return redirect('product-detail', slug=product.slug)
        
        rating = request.POST.get('rating')
        title = request.POST.get('title', '')
        comment = request.POST.get('comment', '')
        
        if not rating:
            messages.error(request, 'Пожалуйста, поставьте оценку')
            return redirect('product-detail', slug=product.slug)
        
        review = Review.objects.create(
            product=product,
            user=request.user,
            rating=int(rating),
            title=title,
            comment=comment
        )
        
        messages.success(request, 'Спасибо за ваш отзыв! Он появится после модерации.')
        return redirect('product-detail', slug=product.slug)