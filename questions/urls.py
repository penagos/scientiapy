from django.urls import path

from . import views

app_name = 'questions'
urlpatterns = [
    path('questions/<int:qid>/', views.view, name="view"),
    path('', views.index, name='index'),
    path('questions/save/<int:qid>/', views.save, name="save"),
    path('questions/new/', views.new, name="new")
]
