from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

def index(request):
    return render(request, template_name='search_bar.html')

def search(request):
    return render(request, 'search_result.html')