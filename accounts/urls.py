from django.urls import path

from . import views


urlpatterns = [
    path('register/', views.signup, name='signup'),
    path('choose-role/', views.choose_role, name='choose_role'),
]
