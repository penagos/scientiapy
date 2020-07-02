from django.urls import path

from . import views

app_name = 'questions'
urlpatterns = [
    path('questions/<int:qid>/', views.view, name="view"),
    path('', views.index, name='index'),
    path('questions/save/', views.save, name="save"),
    path('questions/ask/', views.ask, name="ask"),
    path('questions/new/', views.new, name="new"),
    path('questions/tags/', views.tags, name="tags"),
    path('questions/unanswered/', views.unanswered, name="unanswered"),
    path('questions/edit/<int:pid>/', views.edit, name="edit"),
    path('questions/delete/<int:pid>/', views.delete, name="delete"),
    path('questions/vote/', views.vote, name="vote"),
    path('questions/accept/', views.accept, name="accept"),
]
