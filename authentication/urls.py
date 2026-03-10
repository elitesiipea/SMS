from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', redirection, name="redirection"),
    path('login/', auth_views.LoginView.as_view(template_name='auths/login.html'), name="login"),
    path('logout/', LogoutView.as_view(template_name='auths/login.html'), name='logout'),
    path('password-reset/',auth_views.PasswordResetView.as_view(template_name='auths/password/password_reset.html'), name="password_reset"),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(  template_name='auths/password/password_reset_done.html'), name="password_reset_done"),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view( template_name='auths/password/password_reset_confirm.html'),name="password_reset_confirm"),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='auths/password/password_reset_complete.html'), name="password_reset_complete"),
    path("add/users/", create_user, name="create_user"),
    path("userList/users/", userList, name="list_user"),
    
]