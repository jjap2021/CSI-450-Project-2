import requests
import json

api_key = 'wBj3RyWz9rDaJDt1m5H4O2VKYYgC5P6tWEaYgEqS'

# Endpoint URL
endpoint = 'http://api.eia.gov/v2/electricity/retail-sales/data'

# Parameters
params = {
    'api_key': api_key,
    'data[]': 'sales',  # Specify the data column(s) you want, e.g., 'sales', 'revenue', 'price'
    'facets[stateid][]': 'USA',  # Specify the location facet for USA
    'start': '2020-01-01',  # Specify the start date of the data
    'end': '2020-12-31',  # Specify the end date of the data
    'frequency': 'monthly'  # Specify the frequency of the data
}

# Make the request
response = requests.get(endpoint, params=params)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse JSON response
    energy_consumption_data = response.json()
    # Print the response
    print(json.dumps(energy_consumption_data, indent=2))  # Print the response in a readable JSON format
else:
    print('Failed to retrieve data:', response.status_code)


