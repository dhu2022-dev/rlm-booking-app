import boto3
from botocore.exceptions import ClientError
import json
import time

class AWSDatabaseManager:
    def __init__(self, aws_access_key_id, aws_secret_access_key, region_name, table_name):
        """
        Initialize the AWSDatabaseManager with DynamoDB credentials and table name.
        """
        self.dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
        self.table = self.dynamodb.Table(table_name)

    def get_cached_results(self, artist_name):
        """
        Retrieve cached results for an artist from DynamoDB.
        """
        try:
            print(f"Fetching results for artist: {artist_name}")
            response = self.table.get_item(Key={'artist_name': artist_name})
            print(f"Response from DynamoDB: {response}")

            if 'Item' in response:
                data = response['Item'].get('data')
                print(f"Data retrieved: {data}")

                # Only convert JSON data to Python dictionary if it's a string
                if isinstance(data, str):
                    try:
                        response['Item']['data'] = json.loads(data)
                        print(f"Data after JSON parsing: {response['Item']['data']}")
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON: {e}")
                        return None
                return response['Item']
            return None
        except ClientError as e:
            print(f"Error getting cached results: {e.response['Error']['Message']}")
            return None


    def cache_results(self, artist_name, data):
        """
        Cache new results for an artist in DynamoDB.
        """
        try:
            json_data = json.dumps(data)
            print(f"Caching data for {artist_name}: {json_data}")

            self.table.put_item(
                Item={
                    'artist_name': artist_name,
                    'data': json_data,
                    'timestamp': int(time.time())
                }
            )
            print(f"Cached results for {artist_name}")
        except ClientError as e:
            print(f"Error caching results: {e.response['Error']['Message']}")


    # Add more functions as needed (e.g., update, delete, query)