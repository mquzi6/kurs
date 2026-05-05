from django.contrib import admin
from django.utils import timezone
from .models import Cart, CartItem, Order, OrderItem, Wishlist, Review

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'user', 'get_item_count', 'get_total_price', 'created_at', 'updated_at']
    list_filter = ['created_at']
    search_fields = ['session_key', 'user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity', 'get_total_price', 'added_at']
    list_filter = ['added_at']
    search_fields = ['product__title']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'get_total_items', 'total', 'status', 'payment_status', 'delivery_method', 'created_at']
    list_filter = ['status', 'payment_status', 'delivery_method', 'payment_method', 'created_at']
    search_fields = ['order_number', 'user__username', 'user__email', 'first_name', 'last_name', 'email', 'phone']
    readonly_fields = ['order_number', 'created_at', 'updated_at', 'paid_at', 'shipped_at', 'delivered_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('order_number', 'user', 'status', 'payment_status')
        }),
        ('Контактная информация', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Доставка', {
            'fields': ('delivery_method', 'delivery_address', 'tracking_number')
        }),
        ('Оплата', {
            'fields': ('payment_method',)
        }),
        ('Цены', {
            'fields': ('subtotal', 'delivery_price', 'discount', 'total')
        }),
        ('Дополнительно', {
            'fields': ('notes',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at', 'paid_at', 'shipped_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled']
    
    def mark_as_processing(self, request, queryset):
        queryset.update(status='processing')
    mark_as_processing.short_description = 'Отметить как "В обработке"'
    
    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped', shipped_at=timezone.now())
    mark_as_shipped.short_description = 'Отметить как "Отправлен"'
    
    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered', delivered_at=timezone.now())
    mark_as_delivered.short_description = 'Отметить как "Доставлен"'
    
    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
    mark_as_cancelled.short_description = 'Отметить как "Отменен"'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'title', 'price', 'quantity', 'total']
    list_filter = ['order__status']
    search_fields = ['title', 'order__order_number']

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'added_at']
    list_filter = ['added_at']
    search_fields = ['user__username', 'product__title']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'rating', 'created_at']
    search_fields = ['product__title', 'user__username', 'comment']
    readonly_fields = ['created_at']
    
    actions = ['approve_reviews', 'disapprove_reviews']
    
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
    approve_reviews.short_description = 'Одобрить выбранные отзывы'
    
    def disapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)
    disapprove_reviews.short_description = 'Снять одобрение с выбранных отзывов'