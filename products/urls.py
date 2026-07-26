from django.urls import path

from . import views


urlpatterns = [
    path('create/', views.create_product, name='create_product'),
    path('analytics/', views.seller_analytics, name='seller_analytics'),
    path('<int:product_id>/edit/', views.edit_product, name='edit_product'),
    path('<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('<slug:slug>/', views.product_detail, name='product_detail'),
    path('<slug:slug>/whatsapp/', views.whatsapp_redirect, name='whatsapp_redirect'),
    path('<slug:slug>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('<slug:slug>/review/', views.create_or_update_review, name='create_or_update_review'),
]
