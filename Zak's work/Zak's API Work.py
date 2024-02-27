import requests
import json
import pandas as pd
import folium 
import webbrowser
import jenkspy 
import geopandas as gpd
url = 'https://api.eia.gov/v2/electricity/electric-power-operational-data/data/?frequency=monthly&data[0]=total-consumption-btu&facets[fueltypeid][]=ALL&facets[fueltypeid][]=AOR&facets[fueltypeid][]=COW&facets[fueltypeid][]=FOS&facets[fueltypeid][]=NGO&facets[fueltypeid][]=SUN&facets[fueltypeid][]=WND&facets[sectorid][]=99&facets[location][]=AK&facets[location][]=AL&facets[location][]=AR&facets[location][]=AZ&facets[location][]=CA&facets[location][]=CO&facets[location][]=CT&facets[location][]=DC&facets[location][]=DE&facets[location][]=FL&facets[location][]=GA&facets[location][]=HI&facets[location][]=IA&facets[location][]=ID&facets[location][]=IL&facets[location][]=IN&facets[location][]=KS&facets[location][]=KY&facets[location][]=LA&facets[location][]=MA&facets[location][]=MD&facets[location][]=ME&facets[location][]=MI&facets[location][]=MN&facets[location][]=MO&facets[location][]=MS&facets[location][]=MT&facets[location][]=NC&facets[location][]=ND&facets[location][]=NE&facets[location][]=NH&facets[location][]=NJ&facets[location][]=NM&facets[location][]=NV&facets[location][]=NY&facets[location][]=OH&facets[location][]=OK&facets[location][]=OR&facets[location][]=PA&facets[location][]=PR&facets[location][]=RI&facets[location][]=SC&facets[location][]=SD&facets[location][]=TN&facets[location][]=TX&facets[location][]=US&facets[location][]=UT&facets[location][]=VA&facets[location][]=VT&facets[location][]=WA&facets[location][]=WI&facets[location][]=WV&facets[location][]=WY&start=2022-01&end=2023-01&sort[0][column]=location&sort[0][direction]=asc&offset=0&length=5000&api_key=u7e5iYnTkIJ7cwq2emALYbwgolqCG7DKuXRpaHPC'
#This downloads the json file and loads it via the json library
with requests.get(url, stream = True) as myfile:
    open("Energy", "wb").write(myfile.content)
f = open("Energy")
d = json.load(f)

#This sets up a pandas dataframe and sorts it to be more readable. 
df = pd.DataFrame(d["response"]["data"])
df.sort_values(by=['period', 'location', 'fueltypeid'])
df['total-consumption-btu'] = pd.to_numeric(df['total-consumption-btu'], errors='coerce')
# TypeError: agg function failed [how->mean,dtype->object]
# Originally got this error, put it into ChatGPT and realized that some of the data was NULL 
# Used this line to change all of the objects to numeric data type
# The null types are put to zero
df['total-consumption-btu'] = df['total-consumption-btu'].fillna(0)
piv = pd.pivot_table(df, index=['period', 'location'], columns = ['fuelTypeDescription'], values = ['total-consumption-btu'])
# This will create an interactive map. I was thinking we could plot points of the plants that use the most electricity
# Perhaps use color to show the places with the highest concentration of energy plants
# https://autogis-site.readthedocs.io/en/latest/lessons/lesson-5/interactive-maps.html
# Can we use the sectroid number to plot the electricity generation by sectroid
piv = piv.drop(index='US', level= 1)
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 500)
# print(piv.columns.get_level_values(1))
state_geo = requests.get(
    "https://raw.githubusercontent.com/python-visualization/folium-example-data/main/us_states.json"
).json()
response = requests.get(
    "https://gist.githubusercontent.com/tvpmb/4734703/raw/"
    "b54d03154c339ed3047c66fefcece4727dfc931a/US%2520State%2520List"
)
abbrs = pd.read_json(response.text)

abbrs.head(3)
states_id = gpd.GeoDataFrame.from_features(state_geo, crs="EPSG:4326")
statesmerge = states_id.merge(abbrs, how="left", left_on="name", right_on="name")
statesmerge["geometry"] = statesmerge.geometry.simplify(0.05)
print(statesmerge.head())
# with requests.get('https://raw.githubusercontent.com/python-visualization/folium-example-data/main/us_states.json', stream = True) as Myfile:
#     open("States", "wb").write(Myfile.content)
# h = open("States")
# s = json.load(h)
# p = gpd.read_file('https://raw.githubusercontent.com/python-visualization/folium-example-data/main/us_states.json')
# geo = pd.json_normalize(s['features'], max_level=0)

# # The combining of the staes data and the energy data is a remnant of trying a different method, but it works in getting rid of the 'US' column, so I left it in
# p = p.rename({'id': 'location'}, axis=1)
# states = df.join(p.set_index('location'), on='location', validate = 'm:1')
# print(states.head())
interactive_map = folium.Map(
    location=(39.202257, -75.952992),
    zoom_start=10,
    control_scale=True
)
# piv_reset = piv.reset_index()
# statesmerge = states_id.merge(df, how="left", left_on="id", right_on="location")
# print(statesmerge.head())
piv['ind'] = piv.index.get_level_values('location')
piv['time'] = piv.index.get_level_values('period')
aggregated_data = piv.groupby('ind')[['total-consumption-btu', 'fossil fuels']].sum().reset_index()

# Merge with statesmerge DataFrame
statesmerge = statesmerge.merge(
    aggregated_data,
    how="left",
    left_on="alpha-2",
    right_on="ind",
)

# Assign the merged values to the "total-consumption" column in statesmerge
statesmerge["total-consumption"] = statesmerge["total-consumption-btu"]
cho = folium.Choropleth(
    geo_data=state_geo, #set the reference for the states
    name="Fossil Fuels", #graph name
    data=piv.loc['2022-01'], #Only have this set to one month out of the data set for now, will change with the slider
    columns=['ind',('total-consumption-btu', 'fossil fuels')], #first value is the states, and the second is the values
    key_on="feature.id", #Don't change this
    fill_color="OrRd", #Color palette
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Fossil Fuels Consumption", 
    # bins=10, #Change this for having only specific number of colors
    bins = [0,50, 100, 150, 200, 260],
    # use_jenks=True #Added because the US row skews the data
)
cho.add_to(interactive_map)
ch =folium.Choropleth(
    geo_data=state_geo,
    name="Coal Products",
    data=piv.loc['2022-01'],
    columns=['ind',('total-consumption-btu', 'all coal products')],
    key_on="feature.id",
    fill_color="OrRd",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Coal Products",
    # bins=10,
    bins= [0, 20, 40, 60, 80, 100]
    # use_jenks=True
)
ch.add_to(interactive_map)
cp = folium.Choropleth(
    geo_data=state_geo,
    name="Natural Gas & Other Gases",
    data=piv.loc['2022-01'],
    columns=['ind',('total-consumption-btu', 'natural gas & other gases')],
    key_on="feature.id",
    fill_color="OrRd",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Natural Gas & Other Gases",
    # bins=10,
    # use_jenks=True
    bins= [0, 40, 80, 120, 160, 200]
)
cp.add_to(interactive_map)
# geo_json_ = folium.GeoJson(
#     piv,
#     tooltip = folium.GeoJsonTooltip(
#         fields=['ind', ('total-consumption-btu', 'fossil fuels')],
#         aliases=["State:", "Fossil Fuels Consumption"],
#         localize=True,
#         sticky=False,
#         labels=True,
#         style="""
#             background-color: #F0EFEF;
#             border: 2px solid black;
#             border-radius: 3px;
#             box-shadow: 3px;
#         """,
#         max_width=800,
#     )
# )
# geo_json_.add_to(interactive_map)
# popup = folium.GeoJsonPopup(
#     fields=['ind', ('total-consumption-btu', 'natural gas & other gases')],
#     aliases=["State", "Total Consumption"],
#     localize=True,
#     labels=True,
#     style="background-color: yellow;",
# )
# g = folium.GeoJson(
#     piv.loc['2022-01'],
#     tooltip=tooltip,
#     popup=popup,
# ).add_to(interactive_map)
# tooltip = folium.GeoJsonTooltip(
#     fields=['location', ('total-consumption-btu', 'natural gas & other gases')],
#     aliases=["State:", "Fossil Fuels Consumption"],
#     localize=True,
#     sticky=False,
#     labels=True,
#     style="""
#         background-color: #F0EFEF;
#         border: 2px solid black;
#         border-radius: 3px;
#         box-shadow: 3px;
#     """,
#     max_width=800,
# )

# folium.GeoJson(
#     states,
#     tooltip=tooltip
# ).add_to(interactive_map)
folium.LayerControl().add_to(interactive_map) 
html_path = "fossilfuels_map.html"
interactive_map.save("fossilfuels_map.html")
# html_path = "fossilfuels_map.html"
webbrowser.open(html_path)
# Select specific fuel type. Fossil Fuel and can add layers upon layers
