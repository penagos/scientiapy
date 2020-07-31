from django.contrib.auth import authenticate, logout, login as auth_login
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from questions.models import Post
from user.models import Profile, Setting

# Create your views here.
def activate(request):
    return JsonResponse({'success': True})


def login(request): 
    # Handle both POST and GET requests
    if request.method == "POST":
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            # Successful login
            auth_login(request, user)
            return JsonResponse({'success': True})
        else:
            # Failure
            return JsonResponse({'success': False, 'message': 'Could not log you in'})

        
    else:
        context = {}
        return render(request, 'user/login.html', context)

def join(request):
    # If logged in, redirect to index
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('questions:index'))
    else:
        # Handle post requests for new users
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            password2 = request.POST['password2']
            email = request.POST['email']

            user = User.objects.create_user(username, email, password)
            user.save()

            user = authenticate(username=username,password=password)
            auth_login(request, user)
            return redirect('questions:index')
        else:
            context = {}
            return render(request, 'user/join.html', context)

def logoff(request):
    logout(request)
    return redirect('/')

def forgotpassword(request):
    context = {}
    return render(request, 'user/forgotpassword.html', context)

def profile(request, uid):
    user = get_object_or_404(User, pk=uid)
    user.profile = Profile.objects.get_or_create(user=user)[0]
    recentQuestions = Post.getRecentQuestionsByUser(uid, 5)
    recentAnswers = Post.getRecentAnswersByUser(uid, 5)

    context = {'user': user,
               'recentQuestions': recentQuestions,
               'recentAnswers': recentAnswers}
    return render(request, 'user/profile.html', context)

def settings(request, uid):
    if not request.user.is_authenticated:
        raise PermissionDenied
    else:
        if request.method == "POST":
            receiveDigests = request.POST['receive_digests']

            setting = get_object_or_404(Setting, pk=request.user.id)
            setting.receive_digests = receiveDigests
            setting.save()

            return HttpResponseRedirect(reverse('user:settings', args=(request.user.id,)))
        else:
            context = {'uid': uid}
            return render(request, 'user/settings.html', context)