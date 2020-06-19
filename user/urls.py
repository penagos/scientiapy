from django.urls import path

from . import views

# Namespace
app_name = 'user'
urlpatterns = [
    path('login/', views.login, name='login'),
    path('join/', views.join, name='join'),
    path('logout/', views.logoff, name='logout')
]