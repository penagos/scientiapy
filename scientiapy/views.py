from django.shortcuts import render


# Create your views here.
def about(request):
    context = {}
    return render(request, 'scientiapy/about.html', context)
