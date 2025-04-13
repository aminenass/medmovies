from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
        path('login_in/', views.login_in, name="login"),
        path('logout', views.logout_view, name="logout"),
        path('register/', views.register_user, name="register"),
        path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
        path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
        path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
        path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
] 