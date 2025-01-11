from django.shortcuts import render

# Homepage route
def home(request):
    return render(request, 'event_management/index.html')

