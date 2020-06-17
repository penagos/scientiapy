from django.shortcuts import render

# Create your views here.
def login(request):
    context = {}
    return render(request, 'user/login.html', context)

def join(request):
    context = {}
    return render(request, 'user/join.html', context)