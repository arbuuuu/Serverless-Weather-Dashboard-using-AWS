import json
import urllib3
import os

# --- 1. SET YOUR DETAILS HERE ---
# Store your API key in Lambda Environment Variables, not in code!
# Key: API_KEY, Value: 'your-actual-key'
API_KEY = os.environ.get('API_KEY', '') 
# --- ------------------------ ---

http = urllib3.PoolManager()

def lambda_handler(event, context):
    
    # --- 2. Get city from the API Gateway query string ---
    # The frontend will call: .../weather?city=London
    # API Gateway passes this in event['queryStringParameters']
    try:
        # Get the 'city' parameter from the query string
        city = event['queryStringParameters']['city']
        if not city:
            raise KeyError
    except (KeyError, TypeError):
        # If 'city' is missing or 'queryStringParameters' is None
        print("Missing 'city' query parameter")
        return {
            'statusCode': 400, # Bad Request
            'headers': {
                'Access-Control-Allow-Origin': '*' # IMPORTANT: CORS header
            },
            'body': json.dumps({'message': "Missing 'city' query parameter."})
        }

    # --- 3. Get Weather Data ---
    print(f"Fetching weather data for: {city}")
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    
    try:
        r = http.request('GET', url)
        # Check if the API call was successful
        if r.status != 200:
            print(f"OpenWeather API Error: {r.status}")
            error_data = json.loads(r.data.decode('utf-8'))
            return {
                'statusCode': r.status,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps(error_data) # Pass the API's error message back
            }
            
        # This is the weather data as a Python dict
        data = json.loads(r.data.decode('utf-8'))
        print(f"Successfully fetched data: {data['name']}")
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        return {'statusCode': 500, 'headers': {'Access-Control-Allow-Origin': '*'}, 'body': json.dumps(f"Error fetching data: {e}")}
    
    # --- 4. Return Data Directly to the Browser ---
    # We are no longer saving to S3.
    # We return the data as the function's response.
    return {
        'statusCode': 200,
        'headers': {
            # This 'CORS' header is CRITICAL for your website to read the data
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        },
        'body': json.dumps(data) # Convert the Python dict back to a JSON string
    }