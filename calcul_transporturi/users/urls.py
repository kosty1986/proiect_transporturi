
from django.urls import path
from .views import register, profile, login_view, activate,approve_user_view,resend_activation_email,user_list_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', register, name='register'),
    path('profile/', profile, name='profile'),
    path('login/', login_view, name='login'),
    path('activate/<uuid:token>/', activate, name='activate'),
    path('resend_activation_email/<int:user_id>/', resend_activation_email, name='resend_activation_email'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('approve-user/<int:user_id>/', approve_user_view, name='approve_user'),
    path('', user_list_view, name='user_list'),
]
