from datetime import datetime
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
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
    page_obj = list(paginator.get_page(page_number))

    # Convert comma separated tags to list for easy display
    for post in page_obj:
        if post.tags is not None and post.tags is not '':
            post.tags = post.tags.split(',')

    context = {'questions': page_obj, 'count': questions.count}
    return render(request, 'questions/index.html', context)

def view(request, qid):
    question = get_object_or_404(Post, pk=qid)
    posts = Post.getPosts(qid)

    # Make tags iterable for easy display
    if question.tags is not None:
        question.tags = question.tags.split(',')

    # Fetch related questions
    related = Post.getRelated(question)

    context = {'question': question,
               'answers': posts,
               'related': related}
    return render(request, 'questions/view.html', context)

def vote(request):
    # User must be logged in
    if not request.user.is_authenticated:
        raise PermissionDenied
    else:
        # Find post, update vote count
        # TODO: do not let a user vote more than once
        # TODO: add error handling
        pid = request.POST['pid']
        voteType = int(request.POST['type'])
        post = get_object_or_404(Post, pk=pid)

        if voteType == 1:
            voteType = 1
            post.votes += 1
        else:
            voteType = -1
            post.votes -= 1

        post.save()
        return JsonResponse({'success': True,
                             'type': voteType})

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
        tags = request.POST.get('tags', "").lower()

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

            post.body = body
            post.edit_date = datetime.now()
            post.tags = handleTags(post, tags)
            post.author_edit = request.user

            post.save()
            anchor = '#p' + str(pid)
        elif qid == 0:
            # New question
            name = request.POST['title']
            question = Post(title=name,
                            body=body,
                            author=request.user,
                            post_type=PostType.QUESTION)

            question.save()
            question.tags = handleTags(question, tags)
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

def ask(request):
    context = {'action': 'New Question', 'isNewQuestion': True}
    return render(request, 'questions/edit.html', context)

def new(request):
    context = {}
    return render(request, 'questions/edit.html', context)

def unanswered(request):
    context = {}
    return render(request, 'questions/edit.html', context)

def edit(request, pid):
    # Ensure user is logged in
    if not request.user.is_authenticated:
        raise PermissionDenied
    else:
        post = get_object_or_404(Post, pk=pid)

        if post.post_type == PostType.ANSWER:
            action = 'Editing Answer'
        else:
            action = 'Editing Question'

        if post.tags is None:
            post.tags = ''

        context = {'post': post, 'action': action}
        return render(request, 'questions/edit.html', context)

# Utility functions
def handleTags(post, tags):
    # Handle tags
    if tags != '':
        tagsSplit = tags.split(',')
        for tag in tagsSplit:
            Post.updateTag(post, tag)
    
    return tags