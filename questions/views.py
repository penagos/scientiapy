from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from .models import Question

# Create your views here.
def index(request):
    questions = Question.objects.all
    context = {'questions': questions}
    return render(request, 'questions/index.html', context)

def view(request, qid):
    question = get_object_or_404(Question, pk=qid)
    context = {'question': question}
    return render(request, 'questions/view.html', context)