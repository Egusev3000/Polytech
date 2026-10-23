from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('casino/', views.casino_view, name='casino'),
    path('casino/action/', views.casino_action_view, name='casino_action'),
    path('deposit/', views.deposit_view, name='deposit'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile_view, name='profile'),
    path('logout/', views.logout_view, name='logout'),
    path('ai/', views.polytech_ai_view, name='polytech_ai'),
]
