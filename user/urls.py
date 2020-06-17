from django.urls import path

from . import views

# Namespace
app_name = 'user'
urlpatterns = [
    path('login/', views.login, name='login')
]