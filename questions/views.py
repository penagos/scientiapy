from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from .models import Post, Question

# Create your views here.
def index(request):
    questions = Question.objects.all
    context = {'questions': questions}
    return render(request, 'questions/index.html', context)

def view(request, qid):
    question = get_object_or_404(Question, pk=qid)

    # Fetch all posts which are tied to this question
    posts = Post.objects.filter(question=question.id)
    context = {'question': question, 'posts': posts}
    return render(request, 'questions/view.html', context)

def save(request, qid):
    # User must be logged in
    if request.user.is_authenticated:
        raise PermissionDenied
    else:
        # Posted to when there is a new post or an edit
        question = get_object_or_404(Question, pk=qid)

        # Perform validation on post
        body = request.POST['post']
        post = Post(question=question, body=body)
        post.save()

        return HttpResponseRedirect(reverse('questions:view', args=(question.id,)))

def new(request):
    context = {}
    return render(request, 'questions/new.html', context)