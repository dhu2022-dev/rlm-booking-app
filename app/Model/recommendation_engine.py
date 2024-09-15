def predict_ticket_sales(artist_popularity, venue_capacity): #enhance later with real data and learning models
    # Simple heuristic: The more popular the artist, the higher percentage of tickets sold.
    popularity_factor = artist_popularity / 100  # Convert to a factor between 0 and 1
    estimated_sales = int(venue_capacity * popularity_factor * 0.8)  # Assume 80% of venue capacity for popular artists
    return estimated_sales

# def suggest_ticket_price(predicted_sales, venue_capacity, base_price=50):
#     # If the predicted sales exceed 80% of capacity, increase the price
#     demand_factor = predicted_sales / venue_capacity
    
#     # Adjust price based on demand (simple heuristic)
#     if demand_factor > 0.8:
#         suggested_price = base_price * 1.5  # 50% increase for high demand
#     elif demand_factor > 0.5:
#         suggested_price = base_price * 1.2  # 20% increase for moderate demand
#     else:
#         suggested_price = base_price  # Keep base price for low demand
    
#     return round(suggested_price, 2)

import requests

# Replace with your Azure ML web service endpoint and key
AZURE_ENDPOINT = 'https://<your-azure-endpoint>.azurewebsites.net/score'
AZURE_KEY = '<your-azure-key>'

def call_azure_ml_model(artist_name):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {AZURE_KEY}'
    }
    
    # Format the input data as per model requirements
    input_data = {
        "data": [
            {
                "artist_name": artist_name
            }
        ]
    }
    
    response = requests.post(AZURE_ENDPOINT, json=input_data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        # Modify this line to match the actual structure of your response
        predicted_price = result.get('predictedPrice', 'No prediction available')
        return predicted_price
    else:
        raise Exception(f"Azure ML service call failed with status code {response.status_code}")
