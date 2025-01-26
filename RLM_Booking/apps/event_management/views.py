import json
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.dateparse import parse_date
from .models import Event
from django.views.decorators.csrf import csrf_exempt

# Homepage route
def home(request):
    return render(request, 'event_management/index.html')

def calendar_view(request):
    return render(request, 'event_management/calendar.html')

@csrf_exempt
def save_event(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            event_name = data.get('name')
            event_location = data.get('location')
            event_date = parse_date(data.get('date'))

            if not event_name or not event_location or not event_date:
                return JsonResponse({'error': 'Invalid event data'}, status=400)

            Event.objects.create(name=event_name, location=event_location, date=event_date)
            return JsonResponse({'message': 'Event saved successfully!'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def get_events(request):
    if request.method == 'GET':
        # Query the database for all events
        events = Event.objects.all().values('id', 'name', 'location', 'date')
        return JsonResponse(list(events), safe=False)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def delete_event(request, event_id):
    if request.method == 'DELETE':
        try:
            # Delete the event from the database
            event = Event.objects.get(id=event_id)
            event.delete()
            return JsonResponse({'message': 'Event deleted successfully!'})
        except Event.DoesNotExist:
            return JsonResponse({'error': 'Event not found'}, status=404)
    return JsonResponse({'error': 'Invalid request method'}, status=405)