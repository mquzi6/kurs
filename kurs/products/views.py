from django.views.generic import ListView, DetailView
from django.db.models import Avg
from .models import Product, Category

class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        qs = Product.objects.filter(is_active=True).select_related('category')
        q = self.request.GET.get('q')
        cat = self.request.GET.get('category')
        if q:
            qs = qs.filter(title__icontains=q)
        if cat and cat != 'all':
            qs = qs.filter(category__slug=cat)
        return qs.order_by('-id')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = Category.objects.all()
        return ctx

class ProductDetailView(DetailView):
    """Детальная страница товара"""
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related('category')
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        product = self.object
        
        # Получаем одобренные отзывы
        reviews = product.reviews.filter(is_approved=True).select_related('user').order_by('-created_at')
        ctx['reviews'] = reviews
        
        # Считаем средний рейтинг
        avg_rating = product.reviews.filter(is_approved=True).aggregate(Avg('rating'))['rating__avg']
        ctx['avg_rating'] = round(avg_rating, 1) if avg_rating else None
        
        # Получаем похожие товары из той же категории
        similar_products = Product.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(id=product.id)[:4]
        ctx['similar_products'] = similar_products
        
        return ctx