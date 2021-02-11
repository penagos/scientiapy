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
        user = authenticate(username=request.POST['username'],
                            password=request.POST['password'])
        if user is not None:
            # Successful login
            auth_login(request, user)
            return JsonResponse({'success': True})
        else:
            # Failure
            return JsonResponse({
                'success': False,
                'message': 'Could not log you in'
            })
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

            # Make sure passwords match
            if password != password2:
                return JsonResponse({
                    'success': False,
                    'message': 'Passwords must match'
                })

            # Even though the frontend checks this for us, we check again to be
            # on the safe side
            if email == "":
                return JsonResponse({
                    'success': False,
                    'message': 'Email cannot be empty'
                })

            if username == "":
                return JsonResponse({
                    'success': False,
                    'message': 'Username cannot be empty'
                })

            if len(password) < 4:
                return JsonResponse({
                    'success':
                    False,
                    'message':
                    'Password must be at least 4 characters long'
                })

            # Check if username exists
            usr = User.objects.filter(username=username)

            if usr.exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Username already taken'
                })
            else:
                try:
                    user = User.objects.create_user(username, email, password)
                    user.save()
                except:
                    return JsonResponse({
                        'success':
                        False,
                        'message':
                        'An unexpected error occurred'
                    })

                user = authenticate(username=username, password=password)
                auth_login(request, user)
                return JsonResponse({'success': True})
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

    context = {
        'profileUser': user,
        'recentQuestions': recentQuestions,
        'recentAnswers': recentAnswers
    }
    return render(request, 'user/profile.html', context)


def settings(request, uid):
    if not request.user.is_authenticated:
        raise PermissionDenied
    else:
        user = get_object_or_404(User, pk=uid)
        user.profile = Profile.objects.get_or_create(user=user)[0]
        user.setting = Setting.objects.get_or_create(user=user)[0]
        if request.method == "POST":
            if 'receive_digests' in request.POST:
                # Enable
                user.setting.receive_digests = True
            else:
                # Disable
                user.setting.receive_digests = False

            if 'subscribe_all' in request.POST:
                # Enable
                user.setting.subscribe_all = True
            else:
                # Disable
                user.setting.subscribe_all = False

            user.profile.about = request.POST['about']
            user.setting.save()
            user.profile.save()
            return HttpResponseRedirect(
                reverse('user:settings', args=(request.user.id, )) +
                '?success=1')
        else:
            if user.setting.receive_digests:
                receive_digests = 'checked'
            else:
                receive_digests = ''

            if user.setting.subscribe_all:
                subscribe_all = 'checked'
            else:
                subscribe_all = ''

            context = {
                'uid': uid,
                'receive_digests': receive_digests,
                'subscribe_all': subscribe_all,
                'aboutme': user.profile.about,
                'email': user.email
            }
            return render(request, 'user/settings.html', context)


def all(request):
    query = request.GET.get('query')
    users = User.objects.filter(username__icontains=query)
    return JsonResponse([x.username for x in list(users)], safe=False)
