from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from .models import Post, PostType

# Create your views here.
def index(request):
    # If a search was made, filter on needle
    if request.GET.get('q') is not None:
        questions = Post.objects.filter(title__icontains=request.GET['q'], post_type=PostType.QUESTION)
    else:
        questions = Post.objects.filter(post_type=PostType.QUESTION).order_by('-id')

    # TODO: make this setting customizable from admin panel
    paginator = Paginator(questions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'questions': page_obj, 'count': questions.count}
    return render(request, 'questions/index.html', context)

def view(request, qid):
    question = get_object_or_404(Post, pk=qid)
    posts = Post.objects.filter(parent_id=qid)
    context = {'question': question, 'answers': posts}
    return render(request, 'questions/view.html', context)

def save(request):
    # User must be logged in
    if not request.user.is_authenticated:
        raise PermissionDenied
    else:
        # Perform validation on post
        body = request.POST['post']
        pid = request.POST['pid']
        qid = request.POST.get('qid', 0)

        if pid == "":
            pid = 0
        else:
            pid = int(pid)

        # Posted to when there is a new post or an edit. If the post ID is
        # non-zero we are editing. If the question_id is non-zero we are
        # posting a reply. Otherwise we are posting a new question
        if pid:
            # Update existing answer or question
            post = get_object_or_404(Post, pk=pid)

            # If this is a question, update the title
            if post.post_type == PostType.QUESTION:
                post.title = request.POST['title']
                qid = post.id
            else:
                qid = post.parent_id.id

            post.body = request.POST['post']
            post.save()
        elif qid == 0:
            name = request.POST['title'];
            question = Post(title=name,
                            body=body,
                            author=request.user,
                            post_type=PostType.QUESTION)
            question.save()
            qid = question.pk
        else:
            post = Post(author=request.user,
                        body=body,
                        parent_id=get_object_or_404(Post, pk=qid),
                        post_type=PostType.ANSWER)
            post.save()

        return HttpResponseRedirect(reverse('questions:view', args=(qid,)))

def new(request):
    context = {'action': 'New Question', 'isNewQuestion': True}
    return render(request, 'questions/edit.html', context)

def edit(request, pid):
    post = get_object_or_404(Post, pk=pid)

    if post.post_type == PostType.ANSWER:
        action = 'Editing Answer'
    else:
        action = 'Editing Question'

    context = {'post': post, 'action': action}
    return render(request, 'questions/edit.html', context)