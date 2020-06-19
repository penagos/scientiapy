from django.urls import path

from . import views

app_name = 'questions'
urlpatterns = [
    path('questions/<int:qid>/', views.view, name="view"),
    path('', views.index, name='index'),
]
