from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.
def login(request):
    # Handle both POST and GET requests
    if request.method == "POST":
        return JsonResponse({'login': True})
    else:
        context = {}
        return render(request, 'user/login.html', context)

def join(request):
    context = {}
    return render(request, 'user/join.html', context)