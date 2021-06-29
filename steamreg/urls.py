from django.urls import path
from django.contrib.auth import views as auth_views
from .forms import UserPasswordResetForm, UserSetPassowrdForm

from . import views

urlpatterns = [


    #Rregistation
    path('register/', views.register_page, name='register'),
    path('activate/<uidb64>/<token>/',views.activate, name='activate'), 
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_user, name='logout'),

    #Password reset
    path('reset_password/',
        auth_views.PasswordResetView.as_view(
            template_name="steamreg/password_reset.html",
            form_class=UserPasswordResetForm,),
        name="reset_password"),

    path('reset_password/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name="steamreg/password_reset_sent.html",),
        name="password_reset_done"),

    path('reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name="steamreg/password_reset_form.html",
            form_class=UserSetPassowrdForm),
        name="password_reset_confirm"),

    path('reset_password/complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name="steamreg/password_reset_done.html",),
        name="password_reset_complete"),


]