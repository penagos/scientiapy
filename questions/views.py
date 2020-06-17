from django.http import HttpResponse
from django.shortcuts import render
from .models import Question

# Create your views here.
def index(request):
    questions = Question.objects.order_by('-title')[:5]
    context = {'questions': questions}
    context = {}
    return render(request, 'questions/index.html', context)