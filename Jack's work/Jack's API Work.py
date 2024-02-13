# import requests

# api_key = 'wBj3RyWz9rDaJDt1m5H4O2VKYYgC5P6tWEaYgEqS'
# endpoint = 'http://api.eia.gov/v2/series/'

# params = {
#     'api_key': api_key,
#     'series_id': 'ELEC.GEN.ALL-AL-99.A'
# }

# response = requests.get(endpoint, params=params)

# data = response.json()
# print(data)

# if response.status_code != 200:
#     print('Error:', response.status_code)
#     print('Message:', response.text)

import requests

api_key = 'wBj3RyWz9rDaJDt1m5H4O2VKYYgC5P6tWEaYgEqS'

def get_energy_production_data():
    endpoint = 'http://api.eia.gov/v2/series/'
    series_id = 'ELEC.GEN.ALL-US-99.A'
    params = {
        'api_key': api_key,
        'series_id': series_id
    }

    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print('Error:', response.status_code)
        print('Response:', response.text)
        return {'error': 'Failed to retrieve data'}

if __name__ == '__main__':
    energy_production_data = get_energy_production_data()
    print(energy_production_data)
