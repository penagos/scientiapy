from django.urls import path

from . import views

# Namespace
app_name = 'user'
urlpatterns = [
    path('<int:uid>/', views.profile, name='profile'),
    path('all/', views.all, name='all'),
    path('activate/', views.activate, name='activate'),
    path('login/', views.login, name='login'),
    path('join/', views.join, name='join'),
    path('logout/', views.logoff, name='logout'),
    path('forgotpassword/', views.forgotpassword, name='forgotpassword'),
    path('settings/<int:uid>/', views.settings, name='settings')
]