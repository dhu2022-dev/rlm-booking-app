import boto3
import csv
import json

def get_all_items():
    table_name = 'APIResults'
    region_name = 'us-east-1'
    
    dynamodb = boto3.resource('dynamodb', region_name=region_name)
    table = dynamodb.Table(table_name)
    
    items = []
    try:
        response = table.scan()
        items.extend(response.get('Items', []))
        
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))
    
    except Exception as e:
        print(f"Error scanning table: {e}")
    
    print(f"Retrieved {len(items)} items from DynamoDB.")
    return items

def parse_dynamodb_json(items):
    parsed_data = []
    
    for item in items:
        artist_data_str = item.get('data', '[]')
        print(f"Raw artist_data_str: {artist_data_str}")  # Debugging output
        
        try:
            # Check if artist_data_str is valid JSON
            artist_data_list = json.loads(artist_data_str)
            
            # Proceed if it's a list
            if isinstance(artist_data_list, list) and len(artist_data_list) > 0:
                first_artist_data = artist_data_list[0]
                print(f"First artist data: {first_artist_data}")  # Debugging output
                
                if isinstance(first_artist_data, dict):
                    parsed_artist = {
                        'artist_name': first_artist_data.get('name', 'Unknown'),
                        'genre': ', '.join(first_artist_data.get('genres', [])),
                        'popularity': first_artist_data.get('popularity', 'Unknown'),
                        'followers': first_artist_data.get('followers', {}).get('total', 'Unknown'),
                        'external_url': first_artist_data.get('external_urls', {}).get('spotify', 'Unknown')
                    }
                    parsed_data.append(parsed_artist)
                else:
                    print(f"Unexpected data format for artist: {first_artist_data}")
                    
            else:
                # If artist_data_str is not a valid JSON list, handle as plain text
                parsed_artist = {
                    'artist_name': artist_data_str,
                    'genre': 'Unknown',
                    'popularity': 'Unknown',
                    'followers': 'Unknown',
                    'external_url': 'Unknown'
                }
                parsed_data.append(parsed_artist)
                
        except json.JSONDecodeError:
            # Handle as plain text if JSON decoding fails
            parsed_artist = {
                'artist_name': artist_data_str,
                'genre': 'Unknown',
                'popularity': 'Unknown',
                'followers': 'Unknown',
                'external_url': 'Unknown'
            }
            parsed_data.append(parsed_artist)
                
    print(f"Parsed {len(parsed_data)} artist records.")
    return parsed_data

def write_to_csv(parsed_data, filename='output.csv'):
    csv_columns = ['artist_name', 'genre', 'popularity', 'followers', 'external_url']
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            
            for data in parsed_data:
                writer.writerow(data)
                
        print(f"Data successfully written to {filename}")
    
    except IOError as e:
        print(f"I/O error occurred: {e}")

if __name__ == "__main__":
    items = get_all_items()
    parsed_data = parse_dynamodb_json(items)
    write_to_csv(parsed_data)
