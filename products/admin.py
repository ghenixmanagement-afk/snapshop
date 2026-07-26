from django.contrib import admin

from .models import Category, Favorite, Product, ProductAnalytics, Review, SubCategory


class SubCategoryInline(admin.TabularInline):
    model = SubCategory
    extra = 1
    fields = ("name", "slug", "is_active")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'shop', 'category', 'subcategory', 'price', 'in_stock', 'created_at')
    list_filter = ('in_stock', 'category', 'subcategory__category')
    search_fields = ('name', 'shop__name', 'slug', 'category', 'subcategory__name')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = [SubCategoryInline]


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "is_active")
    list_filter = ("is_active", "category")
    search_fields = ("name", "category__name")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'product')


@admin.register(ProductAnalytics)
class ProductAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('product', 'views_count', 'whatsapp_clicks', 'updated_at')
