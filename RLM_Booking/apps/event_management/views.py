from django.http import JsonResponse
from integrations.ticketmaster_api_manager import TicketmasterAPIManager
from django.shortcuts import render
import json
import logging

logger = logging.getLogger(__name__)
ticketmaster = TicketmasterAPIManager()

# Render the main event management page
def event_management_page(request):
    return render(request, 'event_management/event_management_page.html')

def search_events(request):
    if request.method != "GET":
        return JsonResponse({"error": "Invalid request method. Use GET."}, status=405)

    # Get query parameters
    artist = request.GET.get("artist", "").strip()
    postal_code = request.GET.get("zipCode", "").strip()
    radius = request.GET.get("radius", "").strip()
    start_date = request.GET.get("startDate", "").strip()
    end_date = request.GET.get("endDate", "").strip()

    # Log the received parameters
    logger.debug(f"Received search parameters: artist={artist}, postal_code={postal_code}, radius={radius}, start_date={start_date}, end_date={end_date}")

    # Validate radius
    if radius and not radius.isdigit():
        return JsonResponse({"error": "Radius must be a numeric value."}, status=400)

    # Validate start_date and end_date
    try:
        if start_date:
            # Ensure valid date format (Ticketmaster expects YYYY-MM-DD)
            start_date = start_date.strip()
            # You can add further date validation here if necessary

        if end_date:
            end_date = end_date.strip()

    except ValueError as e:
        return JsonResponse({"error": f"Invalid date format: {str(e)}"}, status=400)

    # Ensure at least one search parameter is provided
    if not (artist or postal_code or start_date or end_date):
        return JsonResponse({"error": "At least one search parameter is required."}, status=400)

    try:
        # Fetch events using the Ticketmaster API
        events = ticketmaster.fetch_events(
            artist=artist,
            postalcode=postal_code,
            radius=int(radius) if radius else None,
            start_date=start_date,
            end_date=end_date,
        )

        # Log the raw API response (for debugging purposes)
        logger.debug(f"API response: {events}")

        # Format the response for the frontend
        event_data = [
            {
                "artist": event.get("artist", "Unknown"),
                "name": event.get("name", "Unknown"),
                "venue": event.get("venue", "Unknown"),
                "date": event.get("date", "Unknown"),
                "location": event.get("location", "Unknown"),
            }
            for event in events
        ]

        # Return the formatted response
        return JsonResponse(event_data, safe=False)

    except Exception as e:
        logger.error(f"Error in search_events: {str(e)}", exc_info=True)
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)