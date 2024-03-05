# POWERPLANT CODE

import pandas as pd
import requests
import json
import folium
import webbrowser

api_key = 'O321szCL3xptUGbdazZYEY1HBQ5qtIT0vFev6bTe'
url = f'https://api.eia.gov/v2/electricity/facility-fuel/data/?frequency=monthly&data[0]=total-consumption-btu&start=2022-01&end=2023-12&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000&api_key={api_key}'

with requests.get(url, stream = True) as myfile:
    open("Energy", "wb").write(myfile.content)

with open("Energy", "r") as f:
    d = json.load(f)

df = pd.DataFrame(d["response"]["data"])


# how many power plants does each state have?

# i used .nunique instead of count because if i use count, powerplant get repeated
# https://www.w3schools.com/python/pandas/ref_df_nunique.asp

df.sort_values(by=['state', 'plantCode'], inplace=True)
power_plants_nunique = df.groupby('state')['plantCode'].nunique().reset_index(name='Power Plant Count')

power_plants_count = pd.DataFrame(power_plants_nunique)

print(power_plants_count)


# which powerplants generate the most?

df.drop_duplicates(subset=['plantName', 'state'], inplace=True)
df.sort_values(by='total-consumption-btu', ascending=False, inplace=True)
top_generating_powerplants = df[['plantName', 'state', 'total-consumption-btu']].head(10)

print(top_generating_powerplants)

# choropleth map for number of powerplants for each state

state_geo = requests.get(
    "https://raw.githubusercontent.com/python-visualization/folium-example-data/main/us_states.json"
).json()

interactive_map = folium.Map(
    location=(39.202257, -75.952992),
    zoom_start=4,
    control_scale=True
)

folium.Choropleth(
    geo_data=state_geo,
    name="Power Plants Count",
    data=power_plants_count,
    columns=['state', 'Power Plant Count'],
    key_on="feature.id",
    fill_color="YlGn",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Power Plants Count",
    bins=10, 
    reset=True  
).add_to(interactive_map)

folium.LayerControl().add_to(interactive_map)

interactive_map.save("power_plants_map.html")
html_path = "Energy Consumption/power_plants_map.html"




