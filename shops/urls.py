from django.urls import path

from . import views


urlpatterns = [
    path('dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('manage/', views.create_or_edit_shop, name='manage_shop'),
    path('moderation/', views.moderation_dashboard, name='moderation_dashboard'),
    path('<slug:slug>/', views.shop_public, name='shop_public'),
]
