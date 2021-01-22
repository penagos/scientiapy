from datetime import datetime
from django.contrib.auth.models import User
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.urls import reverse
from itertools import chain
from .models import Comment, Post, PostTag, PostType, Tag, Vote
from user.models import Profile, Setting


# Create your views here.
def index(request):
    # If a search was made, filter on needle
    title = 'Questions'
    subtitle = ''
    searchQuery = ''

    # Handle sorting of results if specified
    sort = request.GET.get('sort', '')

    if sort == 'new':
        sort = '-published_date'
    elif sort == 'hot':
        sort = 'published_date'
    else:
        sort = '-id'

    if request.GET.get('q') is not None:
        # Search across tags, answers and questions
        # Puts questions before answer hits
        query = request.GET.get('q')
        searchQuery = '&q={}'.format(query)
        title = 'Search Results for "{}"'.format(query)

        # Unless search string is quoted, search for each word independently
        quoted = (query[0] == '"' and query[-1] == '"')
        questions = Post.objects.none()

        if quoted:
            query = query[1:-1]
            questions = Post.objects.filter(
                Q(title__icontains=query) | Q(body__icontains=query)
                | Q(tags__icontains=query)).annotate(
                    answers=Count('post')).order_by(sort)
        else:
            queries = query.split()
            for query in queries:
                questions = questions | (Post.objects.filter(
                    Q(title__icontains=query) | Q(body__icontains=query)
                    | Q(tags__icontains=query)).annotate(
                        answers=Count('post')).order_by(sort))

        # Walk result set and prune accordingly
        questionsFiltered = []
        numQuestions = 0
        numAnswers = 0
        for q in questions:
            if q.post_type != PostType.QUESTION.value:
                numAnswers += 1

                # Do not add duplicate results
                if not any(x.id == q.parent_id for x in questionsFiltered):
                    q = Post.objects.filter(pk=q.parent_id).annotate(
                        answers=Count('post')).order_by('-post_type')[0]
                else:
                    q = None
            else:
                if any(x.id == q.id for x in questionsFiltered):
                    q = None

                numQuestions += 1

            if q is not None:
                questionsFiltered.append(q)
        questions = questionsFiltered
        subtitle = f"Matched {numQuestions} questions and {numAnswers} answers"
    elif request.GET.get('tag') is not None:
        query = request.GET.get('tag')
        title = 'Questions tagged "{}"'.format(query)
        questions = Post.objects.filter(
            Q(tags__icontains=query)).annotate(answers=Count('post'))
        searchQuery = '&tag={}'.format(query)
    else:
        questions = Post.objects.filter(post_type=PostType.QUESTION).annotate(
            answers=Count('post')).order_by(sort)

    # Convert comma separated tags to list for easy display
    for post in questions:
        if post.tags is not None and post.tags is not '':
            post.tags = post.tags.split(',')

    # AJAX requests are fulfilled with a JSON response we can return early as
    # we do not need any of the additional processing done below
    if request.GET.get('ajax') is not None:
        response = []

        for post in questions:
            serialized = {}
            serialized['qid'] =  post.id if post.post_type == PostType.QUESTION.value else post.parent.id
            serialized['pid'] = post.id
            serialized['title'] = post.title
            serialized['description'] = (post.body[:150] + '..') if len(post.body) > 150 else post.body
            serialized['tags'] = post.tags
            serialized['url'] = reverse('questions:view', args=(serialized['qid'], ))
            serialized['author'] = post.author.username
            serialized['published_date'] = post.published_date

            response.append(serialized)

        return JsonResponse(response, safe=False)

    # TODO: make this setting customizable from admin panel
    paginator = Paginator(questions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Recent sidebar
    recent = Post.getRecentQuestions()

    # Hot posts sidebar
    hot = Post.getHotQuestions()

    # Unanswered questions sidebar
    unanswered = Post.getUnansweredQuestions()

    # Get some stats for the homepage
    questions_count = Post.getQuestionsCount()
    answers_count = Post.getAnswersCount()
    users_count = User.objects.all().count()

    context = {
        'questions': page_obj,
        'questions_count': questions_count,
        'answers_count': answers_count,
        'users_count': users_count,
        'count': len(questions),
        'title': title,
        'subtitle': subtitle,
        'recent': recent,
        'hot': hot,
        'unanswered': unanswered,
        'query': searchQuery
    }

    return render(request, 'questions/index.html', context)


def view(request, qid):
    question = get_object_or_404(Post, pk=qid)
    posts = Post.getPosts(qid)

    # Make tags iterable for easy display
    if question.tags is not None and question.tags is not '':
        question.tags = question.tags.split(',')

    # Fetch related questions
    related = Post.getRelated(question)

    context = {'question': question, 'answers': posts, 'related': related}
    return render(request, 'questions/view.html', context)


def accept(request):
    # User must be logged in
    if not request.user.is_authenticated:
        raise PermissionDenied
    else:
        pid = request.POST['pid']
        qid = request.POST['qid']
        question = get_object_or_404(Post, pk=qid)
        answer = get_object_or_404(Post, pk=pid)
        question.accepted = answer
        question.accepted_author = request.user
        question.accepted_date = datetime.now()
        question.save()

        # For sorting answers we cache to which question this was accepted for
        answer.accepted = question
        answer.save()
        return JsonResponse({'success': True})


def vote(request):
    # User must be logged in
    if not request.user.is_authenticated:
        raise PermissionDenied
    else:
        # Find post, update vote count
        pid = request.POST['pid']

        # Prevent vote change if one is already registered
        oldVote = Vote.objects.filter(
            Q(post_id=pid) & Q(user_id=request.user.id))

        if not oldVote:
            voteType = int(request.POST['type'])
            post = get_object_or_404(Post, pk=pid)
            user = get_object_or_404(User, pk=post.author.id)
            user.profile = Profile.objects.get_or_create(user=user)[0]

            if voteType == 1:
                voteType = 1
                post.votes += 1
            else:
                voteType = -1
                post.votes -= 1

            post.save()
            user.profile.reputation += voteType
            user.profile.save()

            # Create a new vote entry
            vote = Vote(post=post, user=request.user, amount=voteType)
            vote.save()
        else:
            # Update existing vote
            voteType = 0

        return JsonResponse({'success': True, 'type': voteType})


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

            # If commment ID is set, update existing comment
            cid = request.POST.get('cid', 0)
            if cid:
                cid = int(cid)
                commentStr = comment
                comment = get_object_or_404(Comment, pk=cid)
                comment.body = commentStr
                comment.edit_date = datetime.now()
                comment.author_edit = request.user
            else:
                comment = Comment(post=post, author=request.user, body=comment)

            if post.post_type == PostType.QUESTION:
                qid = post.id
            else:
                qid = post.parent_id

            comment.save()
            anchor = '#c' + str(comment.pk)

            question = get_object_or_404(Post, pk=qid)
            handleNotify(request, question, comment=comment)
        elif pid:
            # Update existing answer or question
            post = get_object_or_404(Post, pk=pid)
            oldNotify = ''
            notify = False

            # If this is a question, update the title
            if post.post_type == PostType.QUESTION:
                notify = True
                oldNotify = post.notify
                post.title = request.POST['title']
                post.notify = request.POST['notify'].lower()
                qid = post.id
            else:
                qid = post.parent_id

            post.body = body
            post.edit_date = datetime.now()
            post.tags = handleTags(post, tags)
            post.author_edit = request.user
            post.save()

            if notify:
                # Send out emails to new people on the notify list if there's
                # any new additions
                handleNotify(request, post, oldNotify=oldNotify)

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
            question.notify = request.POST['notify'].lower()
            question.save()
            qid = question.pk
            anchor = '#p' + str(qid)

            handleNotify(request, question)
        else:
            question = get_object_or_404(Post, pk=qid)
            post = Post(author=request.user,
                        body=body,
                        parent_id=question.id,
                        post_type=PostType.ANSWER)
            post.save()
            anchor = '#p' + str(post.pk)

            # Notify anyone on question notifylist
            handleNotify(request, question, reply=post)

        return HttpResponseRedirect(
            reverse('questions:view', args=(qid, )) + anchor)


def ask(request):
    context = {
        'action': 'New Question',
        'isNewQuestion': True,
        'notifyList': request.user.username
    }
    return render(request, 'questions/edit.html', context)


def new(request):
    context = {}
    return render(request, 'questions/edit.html', context)


def unanswered(request):
    context = {}
    return render(request, 'questions/edit.html', context)


def tags(request):
    # Fetch tags and question counts
    json = request.GET.get('json')

    if json is None:
        tags = PostTag.getAllTags()
        context = {'tags': tags}
        return render(request, 'questions/tags.html', context)
    else:
        # Map resultset to JSON format
        query = request.GET.get('query')
        tags = Tag.objects.filter(title__icontains=query)
        return JsonResponse([x.title for x in list(tags)], safe=False)


def delete(request, pid):
    if not request.user.is_authenticated:
        raise PermissionDenied
    else:
        # IF POST request, proceed to delete post
        if request.method == "POST":
            post = get_object_or_404(Post, pk=pid)
            handleReputationDeletion(post)
            postType = post.post_type
            post.delete()

            # If a question was removed, redirect back to index page, otherwise
            # redirect to question page
            if postType == PostType.QUESTION:
                return HttpResponseRedirect(reverse('questions:index'))
            else:
                return HttpResponseRedirect(
                    reverse('questions:view', args=(post.parent_id, )))
        else:
            post = get_object_or_404(Post, pk=pid)
            context = {'post': post}
            return render(request, 'questions/delete.html', context)


def deleteComment(request, cid):
    if not request.user.is_authenticated:
        raise PermissionDenied
    else:
        comment = get_object_or_404(Comment, pk=cid)
        comment.delete()
        return JsonResponse({'success': True})


def edit(request, pid):
    # Ensure user is logged in
    if not request.user.is_authenticated:
        raise PermissionDenied
    else:
        post = get_object_or_404(Post, pk=pid)

        if post.post_type == PostType.ANSWER:
            action = 'Editing Answer'
            notifyList = ''
        else:
            action = 'Editing Question'
            notifyList = post.notify

        if post.tags is None:
            post.tags = ''

        context = {'post': post, 'action': action, 'notifyList': notifyList}
        return render(request, 'questions/edit.html', context)


def posts(request, qid, order):
    post = get_object_or_404(Post, pk=qid)

    # Return all answers on this post sorted by desired order
    answers = Post.getPosts(post.id)

    if order == 'old':
        # Sort oldest first
        answers = answers.order_by('published_date')
    elif order == 'new':
        # Sort by newest first
        answers = answers.order_by('-published_date')
    elif order == 'votes':
        # Sort by votes (default)
        answers = answers.order_by('-accepted_id', '-votes', 'published_date')
    else:
        # Unknown pattern
        JsonResponse({'success': False, 'message': 'Unknown sort order'})

    # Render HTML serverside to reuse view template
    postsHTML = render_to_string('questions/answers.html', {
        'answers': answers,
        'question': post
    },
                                 request=request)
    return JsonResponse({'success': True, 'posts': postsHTML}, safe=False)


# Utility functions
def handleTags(post, tags):
    # Handle tags
    if tags != '':
        tagsSplit = tags.split(',')
    else:
        # remove all
        tagsSplit = []

    # If we removed tags, update the table accordingly
    Post.removeTags(post, tagsSplit)

    for tag in tagsSplit:
        Post.updateTag(post, tag)

    return tags


def handleNotify(request, post, oldNotify=None, reply=None, comment=None):
    # If any users are on the notifylist, send them an email
    if post.notify != "":
        usersSplit = post.notify.split(',')
        bccList = []
        oldUsers = []

        # Filter out users which were previously notified
        if oldNotify is not None:
            oldUsers = oldNotify.split(',')

        # Append all users on global notify list
        globalNotifyList = Setting.getGlobalNotifyList()

        for user in globalNotifyList:
            bccList.append(user.user.email)

        for user in usersSplit:
            if user not in oldUsers:
                # Ensure this is a valid user
                userHandle = get_object_or_404(User, username=user)

                # Get email, add to running BCC list
                bccList.append(userHandle.email)

        # Choose the right email template and title
        if reply is None and comment is None:
            # New questsion
            subject = '[Coderflow]: ' + post.title
            template = 'email/newQuestion.html'
            home_link = request.build_absolute_uri('/')
            anchor = ''
        elif reply is None:
            # New comment
            subject = '[Coderflow]: RE: ' + post.title
            template = 'email/newComment.html'
            home_link = request.build_absolute_uri(reverse('questions:view', args=(post.id,)))
            anchor = '#c' + str(comment.pk)
            reply = comment
        else:
            # New post
            subject = '[Coderflow]: RE: ' + post.title
            template = 'email/newAnswer.html'
            home_link = request.build_absolute_uri(reverse('questions:view', args=(post.id,)))
            anchor = '#p' + str(post.pk)

        sendNotifyEmail(request, post, subject, template, home_link, anchor, reply, bccList)

def sendNotifyEmail(request, post, subject, template, home_link, anchor, reply, bccList):
    action_link = request.build_absolute_uri(
        reverse('questions:view', args=(post.id, )) + anchor)
    unsubscribe_link = request.build_absolute_uri(
        reverse('user:settings', args=(request.user.id, )))
    message = render_to_string(
        template, {
            'post': post,
            'home_link': home_link,
            'action_link': action_link,
            'reply': reply,
            'unsubscribe_link': unsubscribe_link
        })
    send_mail(subject,
                'Scientiapy notification',
                'noreply@penagos.co',
                bccList,
                fail_silently=False,
                html_message=message)

# This can be called on either an answer or a question. In the cases that it is
# called on a question, take into consideration all answers which have this post
# as a parent
def handleReputationDeletion(post):
    # Build up a list of all answers as well
    posts = [post]

    if post.post_type == PostType.QUESTION:
        answers = Post.objects.filter(parent_id=post.id)
        posts.append([answer.id for answer in answers])

    # Walk the postXvotes table and update the user table votes cache
    votes = Vote.objects.filter(post_id=post.id)

    # Ensure user has a profile obj
    profile = Profile.objects.get_or_create(user=post.author)[0]
    for vote in votes:
        profile.reputation -= vote.amount
        profile.save()
