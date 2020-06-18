from django.http import HttpResponse
from django.shortcuts import render
from .models import Question

# Create your views here.
def index(request):
    questions = Question.objects.all
    context = {'questions': questions}
    return render(request, 'questions/index.html', context)

def view(request, qid):
    context = {}
    return render(request, 'questions/view.html', context)