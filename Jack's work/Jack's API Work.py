import requests

api_key = 'wBj3RyWz9rDaJDt1m5H4O2VKYYgC5P6tWEaYgEqS'
endpoint = 'http://api.eia.gov/v2/series/'

params = {
    'api_key': api_key,
    'series_id': 'ELEC.GEN.ALL-AL-99.A'
}

response = requests.get(endpoint, params=params)

data = response.json()
print(data)

if response.status_code != 200:
    print('Error:', response.status_code)
    print('Message:', response.text)
