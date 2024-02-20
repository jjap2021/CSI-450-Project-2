import requests
import json
url = 'https://api.eia.gov/v2/electricity/electric-power-operational-data/data/?frequency=monthly&data[0]=total-consumption-btu&facets[fueltypeid][]=ALL&facets[fueltypeid][]=AOR&facets[fueltypeid][]=COW&facets[fueltypeid][]=FOS&facets[fueltypeid][]=NGO&facets[fueltypeid][]=SUN&facets[fueltypeid][]=WND&facets[sectorid][]=99&facets[location][]=AK&facets[location][]=AL&facets[location][]=AR&facets[location][]=AZ&facets[location][]=CA&facets[location][]=CO&facets[location][]=CT&facets[location][]=DC&facets[location][]=DE&facets[location][]=FL&facets[location][]=GA&facets[location][]=HI&facets[location][]=IA&facets[location][]=ID&facets[location][]=IL&facets[location][]=IN&facets[location][]=KS&facets[location][]=KY&facets[location][]=LA&facets[location][]=MA&facets[location][]=MD&facets[location][]=ME&facets[location][]=MI&facets[location][]=MN&facets[location][]=MO&facets[location][]=MS&facets[location][]=MT&facets[location][]=NC&facets[location][]=ND&facets[location][]=NE&facets[location][]=NH&facets[location][]=NJ&facets[location][]=NM&facets[location][]=NV&facets[location][]=NY&facets[location][]=OH&facets[location][]=OK&facets[location][]=OR&facets[location][]=PA&facets[location][]=PR&facets[location][]=RI&facets[location][]=SC&facets[location][]=SD&facets[location][]=TN&facets[location][]=TX&facets[location][]=US&facets[location][]=UT&facets[location][]=VA&facets[location][]=VT&facets[location][]=WA&facets[location][]=WI&facets[location][]=WV&facets[location][]=WY&start=2022-01&end=2023-01&sort[0][column]=location&sort[0][direction]=asc&offset=0&length=5000&api_key=u7e5iYnTkIJ7cwq2emALYbwgolqCG7DKuXRpaHPC'
#This downloads the json file and loads it via the json library
with requests.get(url, stream = True) as myfile:
    open("Energy", "wb").write(myfile.content)
f = open("Energy")
d = json.load(f)

#This sets up a pandas dataframe and sorts it to be more readable. 
df = pd.DataFrame(d["response"]["data"])
df.sort_values(by=['period', 'location', 'fueltypeid'])
#Right now, I'm trying to figure out how to combine all rows with the same date
#into one row, with columns for each energy type/usage amount. LMK if you know how
#to go about this!
piv = pd.pivot_table(df, index=['period', 'location'], columns = ['fuelTypeDescription'], values = ['total-consumption-btu'])

import seaborn as sns
sns.lineplot(data = piv, x = 'period', y = ('total-consumption-btu', 'all fuels'), hue = 'location')
#This graph sucks, but I just wanted to show that I pivoted the data and how to actually graph using a multi-index


#Time Slider Documentation https://python-visualization.github.io/folium/latest/user_guide/plugins/timeslider_choropleth.html
#Cloropleth Documentation  https://python-visualization.github.io/folium/latest/getting_started.html


#Creates two new columns that corrospond to the index values
piv['ind'] = piv.index.get_level_values('location')
piv['time'] = piv.index.get_level_values('period')


import folium
import requests
import jenkspy
# GeoJSON that corrosponds states with polygons of that state.
state_geo = requests.get(
    "https://raw.githubusercontent.com/python-visualization/folium-example-data/main/us_states.json"
).json()
#This sets the map extent
m = folium.Map(location=[48, -102], zoom_start=3)

#Each choropleth is a map layer, so iterating over and making one for each type shouldn't be hard
folium.Choropleth(
    geo_data=state_geo, #set the reference for the states
    name="choropleth", #graph name
    data=piv.loc['2022-01'], #Only have this set to one month out of the data set for now, will change with the slider
    columns=['ind',('total-consumption-btu', 'all renewables')], #first value is the states, and the second is the values
    key_on="feature.id", #Don't change this
    fill_color="YlGn", #Color palette
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Renewable Consumption", 
    bins=24, #Change this for having only specific number of colors
    use_jenks=True #Added because the US row skews the data
).add_to(m)

folium.Choropleth(
    geo_data=state_geo,
    name="a",
    data=piv.loc['2022-01'],
    columns=['ind',('total-consumption-btu', 'solar')],
    key_on="feature.id",
    fill_color="YlGn",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Unemployment Rate (%)",
    bins=24,
    use_jenks=True
).add_to(m)
folium.LayerControl().add_to(m) #Adds UI for turning on/off layers

m