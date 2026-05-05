from django.contrib import admin
from .models import Category, Product, ProductImage

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'stock', 'category', 'is_active', 'is_digital', 'created_at']
    list_filter = ['is_active', 'is_digital', 'category', 'created_at']
    search_fields = ['title', 'description', 'sku', 'brand']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'description', 'category')
        }),
        ('Цена и наличие', {
            'fields': ('price', 'old_price', 'stock', 'sku')
        }),
        ('Медиа', {
            'fields': ('image', 'is_digital', 'digital_file')
        }),
        ('Дополнительно', {
            'fields': ('brand', 'specifications', 'is_active')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'is_main', 'created_at']
    list_filter = ['is_main', 'created_at']