from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('pending_approval/', views.pending_approval, name='pending_approval'),
    path('login_redirect/', views.login_redirect, name='login_redirect'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('approve/<int:user_id>/', views.approve_user, name='approve_user'),
    path('reject/<int:user_id>/', views.reject_user, name='reject_user'),
    path('search/', views.search_view, name='search'),
]

