from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import (
    CartView, CartAddView, CartUpdateView, CartRemoveView,
    CheckoutView, OrderDetailView, OrderHistoryView,
    WishlistView, WishlistRemoveView,
    SignupView, ReviewCreateView
)

urlpatterns = [
    # Вход/выход/регистрация
    path('login/', LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('signup/', SignupView.as_view(), name='signup'),
    # Корзина
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/', CartAddView.as_view(), name='cart-add'),
    path('cart/update/<int:item_id>/', CartUpdateView.as_view(), name='cart-update'),
    path('cart/remove/<int:item_id>/', CartRemoveView.as_view(), name='cart-remove'),
    
    # Оформление заказа
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('order/<str:order_number>/', OrderDetailView.as_view(), name='order_detail'),
    path('orders/', OrderHistoryView.as_view(), name='order_history'),
    
    # Список желаний
    path('wishlist/', WishlistView.as_view(), name='wishlist'),
    path('wishlist/add/', WishlistView.as_view(), name='wishlist-add'),
    path('wishlist/remove/<int:product_id>/', WishlistRemoveView.as_view(), name='wishlist-remove'),
    
    # Выход
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Отзывы
    path('review/<int:product_id>/', ReviewCreateView.as_view(), name='review-create'),
]
