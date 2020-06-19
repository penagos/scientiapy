from django.shortcuts import render

# Create your views here.
def termsofservice(request):
    context = {}
    return render(request, 'legal/termsofservice.html', context)

def privacypolicy(request):
    context = {}
    return render(request, 'legal/privacypolicy.html', context)