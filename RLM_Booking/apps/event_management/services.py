from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# API Endpoint
@csrf_exempt
def availability_search(request):
    if request.method == "POST":
        data = json.loads(request.body)
        artist_venue = data.get("artistVenue")
        date_range = data.get("dateRange")

        # Query database for availability
        availability_data = fetch_availability_from_db(artist_venue, date_range)

        return JsonResponse({"availability": availability_data})

# Database Query Logic
def fetch_availability_from_db(artist_venue, date_range):
    # Example query for simplicity
    bookings = Booking.objects.filter(
        artist_or_venue=artist_venue,
        date__range=date_range
    )
    # Logic to calculate available slots
    return [{"date": "2025-01-15", "status": "available"}]

# Error Handling
return JsonResponse({"error": "Invalid request"}, status=400)