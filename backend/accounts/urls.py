from django.urls import path
from .views import RegisterView, LoginView, DemoLoginView, LogoutView, CurrentUserView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('login/', LoginView.as_view(), name='auth_login'),
    path('demo-login/', DemoLoginView.as_view(), name='auth_demo_login'),
    path('logout/', LogoutView.as_view(), name='auth_logout'),
    path('me/', CurrentUserView.as_view(), name='auth_me'),
]
