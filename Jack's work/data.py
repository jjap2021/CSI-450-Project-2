##Took peter's code and messed with it below

import requests
import json
import pandas as pd
import seaborn as sns
import geopandas as gpd
import matplotlib as plt


url = 'https://api.eia.gov/v2/electricity/electric-power-operational-data/data/?frequency=monthly&data[0]=total-consumption-btu&facets[fueltypeid][]=ALL&facets[fueltypeid][]=AOR&facets[fueltypeid][]=COW&facets[fueltypeid][]=FOS&facets[fueltypeid][]=NGO&facets[fueltypeid][]=SUN&facets[fueltypeid][]=WND&facets[sectorid][]=99&facets[location][]=AK&facets[location][]=AL&facets[location][]=AR&facets[location][]=AZ&facets[location][]=CA&facets[location][]=CO&facets[location][]=CT&facets[location][]=DC&facets[location][]=DE&facets[location][]=FL&facets[location][]=GA&facets[location][]=HI&facets[location][]=IA&facets[location][]=ID&facets[location][]=IL&facets[location][]=IN&facets[location][]=KS&facets[location][]=KY&facets[location][]=LA&facets[location][]=MA&facets[location][]=MD&facets[location][]=ME&facets[location][]=MI&facets[location][]=MN&facets[location][]=MO&facets[location][]=MS&facets[location][]=MT&facets[location][]=NC&facets[location][]=ND&facets[location][]=NE&facets[location][]=NH&facets[location][]=NJ&facets[location][]=NM&facets[location][]=NV&facets[location][]=NY&facets[location][]=OH&facets[location][]=OK&facets[location][]=OR&facets[location][]=PA&facets[location][]=PR&facets[location][]=RI&facets[location][]=SC&facets[location][]=SD&facets[location][]=TN&facets[location][]=TX&facets[location][]=US&facets[location][]=UT&facets[location][]=VA&facets[location][]=VT&facets[location][]=WA&facets[location][]=WI&facets[location][]=WV&facets[location][]=WY&start=2022-01&end=2023-01&sort[0][column]=location&sort[0][direction]=asc&offset=0&length=5000&api_key=u7e5iYnTkIJ7cwq2emALYbwgolqCG7DKuXRpaHPC'

# Downloading the json file and loading it via the json library
with requests.get(url, stream=True) as myfile:
    open("Energy", "wb").write(myfile.content)

f = open("Energy")
d = json.load(f)

#Setting up a pandas dataframe and sorting it to be more readable
df = pd.DataFrame(d["response"]["data"])
df.sort_values(by=['period', 'location', 'fueltypeid'], inplace=True)

#Pivot the data to combine rows with the same date
piv = df.pivot_table(index=['period', 'location'], columns='fuelTypeDescription', values='total-consumption-btu', aggfunc='sum')

#Reset index to get 'period' and 'location' as columns
piv.reset_index(inplace=True)

#Fill NaN values with 0
piv.fillna(0, inplace=True)

#print(piv)

us_states = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

# Merge the GeoDataFrame with the pivot DataFrame on 'location'
merged_data = us_states.merge(piv, left_on='name', right_on='location', how='right')

# Plot the choropleth map
fig, ax = plt.subplots(1, 1, figsize=(10, 8))
merged_data.plot(column='all fuels', cmap='OrRd', linewidth=0.8, ax=ax, edgecolor='0.8', legend=True)

# Set the title and labels
ax.set_title('Total Consumption of All Fuels')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')

# Show the plot
plt.show()