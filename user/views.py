from django.contrib.auth import authenticate, logout, login as auth_login
from django.shortcuts import redirect, render
from django.http import JsonResponse

# Create your views here.
def login(request):
    # Handle both POST and GET requests
    if request.method == "POST":
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            # Successful login
            auth_login(request, user);
            return JsonResponse({'success': True})
        else:
            # Failure
            return JsonResponse({'success': False, 'message': 'Could not log you in'})

        
    else:
        context = {}
        return render(request, 'user/login.html', context)

def join(request):
    context = {}
    return render(request, 'user/join.html', context)

def logoff(request):
    logout(request)
    return redirect('/')

def forgotpassword(request):
    context = {}
    return render(request, 'user/forgotpassword.html', context)