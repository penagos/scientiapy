from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate

# Create your views here.
def login(request):
    # Handle both POST and GET requests
    if request.method == "POST":
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            # Successful login
            success = True
        else:
            # Failure
            success = False

        return JsonResponse({'login': success})
    else:
        context = {}
        return render(request, 'user/login.html', context)

def join(request):
    context = {}
    return render(request, 'user/join.html', context)