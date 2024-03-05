import requests
import json
import pandas as pd
import datetime as dt
import folium
from folium.plugins import TimeSliderChoropleth
import branca.element
import os
import geopandas as gpd
import subprocess

url = 'https://api.eia.gov/v2/electricity/electric-power-operational-data/data/?frequency=monthly&data[0]=total-consumption-btu&facets[fueltypeid][]=ALL&facets[fueltypeid][]=AOR&facets[fueltypeid][]=COW&facets[fueltypeid][]=FOS&facets[fueltypeid][]=NGO&facets[fueltypeid][]=SUN&facets[fueltypeid][]=WND&facets[sectorid][]=99&facets[location][]=AK&facets[location][]=AL&facets[location][]=AR&facets[location][]=AZ&facets[location][]=CA&facets[location][]=CO&facets[location][]=CT&facets[location][]=DC&facets[location][]=DE&facets[location][]=FL&facets[location][]=GA&facets[location][]=HI&facets[location][]=IA&facets[location][]=ID&facets[location][]=IL&facets[location][]=IN&facets[location][]=KS&facets[location][]=KY&facets[location][]=LA&facets[location][]=MA&facets[location][]=MD&facets[location][]=ME&facets[location][]=MI&facets[location][]=MN&facets[location][]=MO&facets[location][]=MS&facets[location][]=MT&facets[location][]=NC&facets[location][]=ND&facets[location][]=NE&facets[location][]=NH&facets[location][]=NJ&facets[location][]=NM&facets[location][]=NV&facets[location][]=NY&facets[location][]=OH&facets[location][]=OK&facets[location][]=OR&facets[location][]=PA&facets[location][]=PR&facets[location][]=RI&facets[location][]=SC&facets[location][]=SD&facets[location][]=TN&facets[location][]=TX&facets[location][]=US&facets[location][]=UT&facets[location][]=VA&facets[location][]=VT&facets[location][]=WA&facets[location][]=WI&facets[location][]=WV&facets[location][]=WY&start=2022-01&end=2023-01&sort[0][column]=location&sort[0][direction]=asc&offset=0&length=5000&api_key=u7e5iYnTkIJ7cwq2emALYbwgolqCG7DKuXRpaHPC'
with requests.get(url, stream = True) as myfile:
    open("Energy", "wb").write(myfile.content)
f = open("Energy")
d = json.load(f)


df = pd.DataFrame(d["response"]["data"])
df.sort_values(by=['period', 'location', 'fueltypeid'])

with requests.get('https://raw.githubusercontent.com/python-visualization/folium-example-data/main/us_states.json', stream = True) as Myfile:
    open("States", "wb").write(Myfile.content)
h = open("States")
s = json.load(h)

p = gpd.read_file('https://raw.githubusercontent.com/python-visualization/folium-example-data/main/us_states.json')
geo = pd.json_normalize(s['features'], max_level=0)
p = p.rename({'id': 'location'}, axis=1)
df = df.join(p.set_index('location'), on='location', validate = 'm:1')


# These are the variables that needed to be set up for the loop to function
styledata = {}
layer_list = []
fuel_types = df.loc[:, 'fuelTypeDescription'].tolist()
fuel_types = list(set(fuel_types))

#This adds the per capita consumption
population_df = pd.read_csv("CBP2022.csv")
population_df['2022 population'] = population_df['2022 population'].str.replace(',', '').astype(float)
state_total_consumption = df.groupby('location')['total-consumption-btu'].sum()
df = pd.merge(df, population_df[['State', '2022 population', 'Abbrev.']], left_on='location', right_on='Abbrev.')
df["total-consumption-btu"] = pd.to_numeric(df["total-consumption-btu"])
df['consumption_per_capita'] = (df['total-consumption-btu'] / df['2022 population'])*1000000

#This creates the main output folder
mainpath = f'Energy Consumption'
if not os.path.exists(mainpath):
    os.mkdir(mainpath)
    print("Folder %s created!" % mainpath)

#Loop that generates html maps for each of the fuel types and per capita
for source in fuel_types:
    styledata = {}
    capitadata = {}
    
    # extremes is needed to set the color palette based on the min/max of all states
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
        capita_style = style_base.filter(items=['consumption_per_capita'])
        capita_style.rename({'consumption_per_capita':'color'}, axis='columns', inplace = True)
        capita_style['opacity']=1 #creates opacity column
        capita_style['color'] = state_style['color'].astype(float) #converts data to floats
        capitadata[ids]=capita_style #adds frame to the capitadata dictionary
    from branca.colormap import linear
    max_color = 0
    
    #These loops assign color values and scales for both the regular and per capita data
    for country, data in styledata.items():
        max_color = extremes['total-consumption-btu'].max()
        min_color = extremes['total-consumption-btu'].min()
        cmap = linear.PuRd_09.scale(float(min_color), float(max_color))
        data["color"] = data["color"].apply(cmap)
    styledict = {
        str(country): data.to_dict(orient="index") for country, data in styledata.items()
    }
    
    for country, data in capitadata.items():
        max_color = extremes['consumption_per_capita'].max()
        min_color = extremes['consumption_per_capita'].min()
        cmap = linear.PuRd_09.scale(float(min_color), float(max_color))
        data["color"] = data["color"].apply(cmap)
    capitadict = {
        str(country): data.to_dict(orient="index") for country, data in capitadata.items()
    }
    
    #Creates a folder for the fuel type
    path = f'{mainpath}/{source.title()}'
    if not os.path.exists(path):
        os.mkdir(path)
        print("Folder %s created!" % path)


    t = folium.Map([38, -97], zoom_start=4)
    y = folium.Map([38, -97], zoom_start=4)
    
    #These sections create the time slider layers
    totals = TimeSliderChoropleth(
        p.to_json(),
        styledict=styledict,
        overlay = True,
        name = source,
        show = True
    
    ).add_to(t)
    
    capitas = TimeSliderChoropleth(
        p.to_json(),
        styledict=capitadict,
        overlay = True,
        name = source,
        show = True
    
    ).add_to(y)
    
    
    #These choropleth layers are here to add a legend for the maps
    chloro = folium.Choropleth(
        geo_data=p.to_json(), 
        name="choropleth", 
        data=df.loc[(df['fuelTypeDescription']==source) & (df['period'] == '2022-01'), ['total-consumption-btu', 'location']],#Only have this set to one month out of the data set for now, will change with the slider
        columns=['location', 'total-consumption-btu'], #first value is the states, and the second is the values
        key_on="feature.id", 
        fill_color="PuRd", 
        fill_opacity=0.0,
        line_opacity=0.2,
        legend_name=f"{source} consumption", 
        bins=24, 
        show=False 
    ).add_to(t)
    
    chloro_capita = folium.Choropleth(
        geo_data=p.to_json(), #set the reference for the states
        name="choropleth", #graph name
        data=df.loc[(df['fuelTypeDescription']==source) & (df['period'] == '2022-01'), ['consumption_per_capita', 'location']],#Only have this set to one month out of the data set for now, will change with the slider
        columns=['location', 'consumption_per_capita'], #first value is the states, and the second is the values
        key_on="feature.id", #Don't change this
        fill_color="PuRd", #Color palette
        fill_opacity=0.0,
        line_opacity=0.2,
        legend_name=f"{source} consumption per capita", 
        bins=24, 
        show=False 
    ).add_to(y)
    
    folium.LayerControl().add_to(t)
    folium.LayerControl().add_to(y)
    
    #Saves the htmls to the appropriate folders
    t.save(f'{mainpath}/{source.title()}/{source}.html')
    y.save(f'{mainpath}/{source.title()}/{source}_capita.html')
subprocess.run(["python", "Zak Backup.py"])
subprocess.run(["python", "LEXI NEW.py"])
subprocess.run(["python", "POWERPLANT CODES.py"])
print('Done!')