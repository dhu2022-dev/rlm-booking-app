import csv
import requests
import time

# Constants
TICKETMASTER_API_KEY = 'PKgRHvbfYjxWr7qkOFplRgvBGCFO5ewo'  # Replace with your actual Ticketmaster API key
TICKETMASTER_BASE_URL = 'https://app.ticketmaster.com/discovery/v2/events.json'
MAX_RETRIES = 5
BACKOFF_FACTOR = 2

def get_ticketmaster_data(artist_name):
    """Retrieve ticket sales and price for the most recent event of the artist."""
    url = TICKETMASTER_BASE_URL
    params = {
        'apikey': TICKETMASTER_API_KEY,
        'keyword': artist_name,
        'sort': 'date,desc'
    }
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Extract the most recent event
            events = data.get('_embedded', {}).get('events', [])
            if events:
                most_recent_event = events[0]
                ticket_sales = most_recent_event.get('sales', {}).get('public', {}).get('quantity', 'Unknown')
                if ticket_sales == 'Unknown':
                    # Check if the quantity is available
                    ticket_sales = most_recent_event.get('sales', {}).get('public', {}).get('amount', 'Unknown')
                ticket_price = most_recent_event.get('priceRanges', [{}])[0].get('min', 'Unknown')
                return ticket_sales, ticket_price
            else:
                return 'No events', 'No price'
        
        except requests.exceptions.RequestException as e:
            print(f"Error retrieving data for {artist_name} (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            time.sleep(BACKOFF_FACTOR ** attempt)  # Exponential backoff
        
    return 'Error', 'Error'

def update_csv_with_ticket_data(input_filename='output.csv', output_filename='updated_output.csv'):
    """Update the CSV file with ticket sales and ticket price."""
    rows = []
    
    # Read the existing CSV file
    with open(input_filename, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            artist_name = row['artist_name']
            print(f"Fetching data for artist: {artist_name}")
            
            # Get ticket sales and price from Ticketmaster
            ticket_sales, ticket_price = get_ticketmaster_data(artist_name)
            row['ticket_sales'] = ticket_sales
            row['ticket_price'] = ticket_price
            
            rows.append(row)
    
    # Write the updated data to a new CSV file
    csv_columns = ['artist_name', 'genre', 'popularity', 'followers', 'external_url', 'ticket_sales', 'ticket_price']
    try:
        with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Updated data successfully written to {output_filename}")
    except IOError as e:
        print(f"I/O error occurred: {e}")

if __name__ == "__main__":
    update_csv_with_ticket_data()
