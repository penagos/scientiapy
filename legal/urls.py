from django.urls import path

from . import views

app_name = 'legal'
urlpatterns = [
    path('legal/termsofservice', views.termsofservice, name='termsofservice'),
    path('legal/privacypolicy', views.privacypolicy, name='privacypolicy')
]