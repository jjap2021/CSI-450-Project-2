import requests
import json
import pandas as pd
url = 'https://api.eia.gov/v2/electricity/electric-power-operational-data/data/?frequency=monthly&data[0]=total-consumption-btu&facets[fueltypeid][]=ALL&facets[fueltypeid][]=AOR&facets[fueltypeid][]=COW&facets[fueltypeid][]=FOS&facets[fueltypeid][]=NGO&facets[fueltypeid][]=SUN&facets[fueltypeid][]=WND&facets[sectorid][]=99&facets[location][]=AK&facets[location][]=AL&facets[location][]=AR&facets[location][]=AZ&facets[location][]=CA&facets[location][]=CO&facets[location][]=CT&facets[location][]=DC&facets[location][]=DE&facets[location][]=FL&facets[location][]=GA&facets[location][]=HI&facets[location][]=IA&facets[location][]=ID&facets[location][]=IL&facets[location][]=IN&facets[location][]=KS&facets[location][]=KY&facets[location][]=LA&facets[location][]=MA&facets[location][]=MD&facets[location][]=ME&facets[location][]=MI&facets[location][]=MN&facets[location][]=MO&facets[location][]=MS&facets[location][]=MT&facets[location][]=NC&facets[location][]=ND&facets[location][]=NE&facets[location][]=NH&facets[location][]=NJ&facets[location][]=NM&facets[location][]=NV&facets[location][]=NY&facets[location][]=OH&facets[location][]=OK&facets[location][]=OR&facets[location][]=PA&facets[location][]=PR&facets[location][]=RI&facets[location][]=SC&facets[location][]=SD&facets[location][]=TN&facets[location][]=TX&facets[location][]=US&facets[location][]=UT&facets[location][]=VA&facets[location][]=VT&facets[location][]=WA&facets[location][]=WI&facets[location][]=WV&facets[location][]=WY&start=2022-01&end=2023-01&sort[0][column]=location&sort[0][direction]=asc&offset=0&length=5000&api_key=u7e5iYnTkIJ7cwq2emALYbwgolqCG7DKuXRpaHPC'
with requests.get(url, stream = True) as myfile:
    open("Energy", "wb").write(myfile.content)
f = open("Energy")
d = json.load(f)



import datetime as dt
import folium
from folium.plugins import TimeSliderChoropleth
from folium.plugins import GroupedLayerControl
# Loads the data into a pandas dataframe
df = pd.DataFrame(d["response"]["data"])
df.sort_values(by=['period', 'location', 'fueltypeid'])

#Loads the state data and opens the json in geopandas as a dataframe
import geopandas as gpd
from io import StringIO
with requests.get('https://raw.githubusercontent.com/python-visualization/folium-example-data/main/us_states.json', stream = True) as Myfile:
    open("States", "wb").write(Myfile.content)
h = open("States")
s = json.load(h)
p = gpd.read_file('https://raw.githubusercontent.com/python-visualization/folium-example-data/main/us_states.json')
geo = pd.json_normalize(s['features'], max_level=0)

# The combining of the staes data and the energy data is a remnant of trying a different method, but it works in getting rid of the 'US' column, so I left it in
p = p.rename({'id': 'location'}, axis=1)
df = df.join(p.set_index('location'), on='location', validate = 'm:1')

# These are the variables that needed to be set up for the loop to function
layer_list = []
fuel_types = df.loc[:, 'fuelTypeDescription'].tolist()
fuel_types = list(set(fuel_types))
t = folium.Map([0, 0], zoom_start=2)

#Loop that generates html maps for each of the fuel types
for source in fuel_types:
    # extremes is needed to set the color palette based on the min/max of all states
    styledata = {}
    extremes = df[df['fuelTypeDescription']== source]
    extremes.replace([None, 0.0], inplace=True)
    extremes.fillna(0)
    #This loop makes a style index for each state in a given fuel type
    for ids in geo.index:
        state = geo.iloc[ids, 1] #Grabs the state id and sets it
        style_base = df[df['location']==state] #creates a filtered data set that only has the state
        style_base = style_base[style_base['fuelTypeDescription']==source] #filters the data to the specific fuel type
        style_base['period'] = pd.to_datetime(style_base['period']) #converts the period column to date time
        style_base['period'] = (style_base['period'] - dt.datetime(1970,1,1)).dt.total_seconds().astype(int) #converts datetime to epoch
        style_base.sort_values(by='period', ascending=True, inplace = True)
        style_base.fillna(0, inplace=True)
        style_base.set_index('period', inplace = True) #sets epoch to the time
        style_base.rename({'total-consumption-btu':'color'}, axis='columns', inplace = True) #renames data to color
        state_style = style_base.filter(items=['color']) #creates a sub data set as base for styledict
        state_style['opacity']=1 #creates opacity column
        state_style['color'] = state_style['color'].astype(float) #converts data to floats
        styledata[ids]=state_style #adds frame to the styledata dictionary
    from branca.colormap import linear
    max_color = 0
    
    #This loop sets the values to hex value colors
    for country, data in styledata.items():
        max_color = extremes['total-consumption-btu'].max()
        min_color = extremes['total-consumption-btu'].min()
        cmap = linear.PuRd_09.scale(float(min_color), float(max_color))
        data["color"] = data["color"].apply(cmap)
    
    #This adds the color data from each state into a final style dictionary
    styledict = {
        str(country): data.to_dict(orient="index") for country, data in styledata.items()
    }
    
    #This creates the folium time slider object, plots it, then saves the map as an html
    fg1 = folium.FeatureGroup(name='g1')
    t = folium.Map([0, 0], zoom_start=2)
    y = TimeSliderChoropleth(
        p.to_json(),
        styledict=styledict,
        overlay = True,
        name = source,
        show = False
    
    ).add_to(t)
    folium.LayerControl().add_to(t)
    t.save(f'{source}.html')