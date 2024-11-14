from django.shortcuts import render
from django.urls import path, include

# Homepage route
def home(request):
    return render(request, 'base.html')