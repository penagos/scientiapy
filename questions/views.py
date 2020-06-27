from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from .models import Comment, Post, PostType

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
    posts = Post.getPosts(qid)
    context = {'question': question, 'answers': posts}
    return render(request, 'questions/view.html', context)

def save(request):
    # User must be logged in
    if not request.user.is_authenticated:
        raise PermissionDenied
    else:
        # Perform validation on post
        body = request.POST.get('post', "")
        pid = request.POST['pid']
        qid = request.POST.get('qid', 0)
        comment = request.POST.get('comment', "")

        # Only set for question edits
        tags = request.POST.get('tags', "")

        if pid == "":
            pid = 0
        else:
            pid = int(pid)

        # Posted to when there is a new post or an edit. If the post ID is
        # non-zero we are editing. If the question_id is non-zero we are
        # posting a reply. Otherwise we are posting a new question
        if comment != "":
            post = get_object_or_404(Post, pk=pid)
            comment = Comment(post=post,
                              author=request.user,
                              body=comment)
            comment.save()
            qid = post.parent_id.id
            anchor = '#c' + str(comment.pk)
        elif pid:
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
            anchor = '#p' + str(pid)
        elif qid == 0:
            # New question
            name = request.POST['title'];
            question = Post(title=name,
                            body=body,
                            author=request.user,
                            post_type=PostType.QUESTION)
            question.save()
            qid = question.pk
            anchor = '#p' + str(qid)
        else:
            post = Post(author=request.user,
                        body=body,
                        parent_id=get_object_or_404(Post, pk=qid),
                        post_type=PostType.ANSWER)
            post.save()
            anchor = '#p' + str(post.pk)

        return HttpResponseRedirect(reverse('questions:view', args=(qid,)) + anchor)

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