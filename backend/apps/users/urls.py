from django.urls import path
from .views import (
    ChangePasswordView,
    LoginView,
    LogoutView,
    MeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RegisterView,
    TokenRefreshView,
    UserDetailView,
    UserListView,
)

urlpatterns = [
    path('login/',                    LoginView.as_view(),               name='auth-login'),
    path('logout/',                   LogoutView.as_view(),               name='auth-logout'),
    path('register/',                 RegisterView.as_view(),             name='auth-register'),
    path('refresh/',                  TokenRefreshView.as_view(),         name='auth-refresh'),
    path('me/',                       MeView.as_view(),                   name='auth-me'),
    path('me/password/',              ChangePasswordView.as_view(),       name='auth-password'),
    path('password-reset/',           PasswordResetRequestView.as_view(), name='auth-password-reset'),
    path('password-reset/confirm/',   PasswordResetConfirmView.as_view(), name='auth-password-reset-confirm'),
    path('users/',                    UserListView.as_view(),             name='user-list'),
    path('users/<uuid:pk>/',          UserDetailView.as_view(),           name='user-detail'),
]
