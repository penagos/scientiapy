from django.urls import path

from . import views

app_name = 'questions'
urlpatterns = [
    path('questions/<int:qid>/', views.view, name="view"),
    path('', views.index, name='index'),
    path('questions/save/', views.save, name="save"),
    path('questions/new/', views.new, name="new"),
    path('questions/edit/<int:pid>/', views.edit, name="edit"),
]
