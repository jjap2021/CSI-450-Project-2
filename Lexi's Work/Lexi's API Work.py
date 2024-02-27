import pandas as pd
import requests
import json
url = 'https://api.eia.gov/v2/electricity/electric-power-operational-data/data/?frequency=monthly&data[0]=total-consumption-btu&facets[fueltypeid][]=ALL&facets[fueltypeid][]=AOR&facets[fueltypeid][]=COW&facets[fueltypeid][]=FOS&facets[fueltypeid][]=NGO&facets[fueltypeid][]=SUN&facets[fueltypeid][]=WND&facets[sectorid][]=99&facets[location][]=AK&facets[location][]=AL&facets[location][]=AR&facets[location][]=AZ&facets[location][]=CA&facets[location][]=CO&facets[location][]=CT&facets[location][]=DC&facets[location][]=DE&facets[location][]=FL&facets[location][]=GA&facets[location][]=HI&facets[location][]=IA&facets[location][]=ID&facets[location][]=IL&facets[location][]=IN&facets[location][]=KS&facets[location][]=KY&facets[location][]=LA&facets[location][]=MA&facets[location][]=MD&facets[location][]=ME&facets[location][]=MI&facets[location][]=MN&facets[location][]=MO&facets[location][]=MS&facets[location][]=MT&facets[location][]=NC&facets[location][]=ND&facets[location][]=NE&facets[location][]=NH&facets[location][]=NJ&facets[location][]=NM&facets[location][]=NV&facets[location][]=NY&facets[location][]=OH&facets[location][]=OK&facets[location][]=OR&facets[location][]=PA&facets[location][]=PR&facets[location][]=RI&facets[location][]=SC&facets[location][]=SD&facets[location][]=TN&facets[location][]=TX&facets[location][]=US&facets[location][]=UT&facets[location][]=VA&facets[location][]=VT&facets[location][]=WA&facets[location][]=WI&facets[location][]=WV&facets[location][]=WY&start=2022-01&end=2023-01&sort[0][column]=location&sort[0][direction]=asc&offset=0&length=5000&api_key=u7e5iYnTkIJ7cwq2emALYbwgolqCG7DKuXRpaHPC'
#This downloads the json file and loads it via the json library
with requests.get(url, stream = True) as myfile:
    open("Energy", "wb").write(myfile.content)
f = open("Energy")
d = json.load(f)

df = pd.DataFrame(d["response"]["data"])
df.sort_values(by=['period', 'location', 'fueltypeid'])
#Right now, I'm trying to figure out how to combine all rows with the same date
#into one row, with columns for each energy type/usage amount. LMK if you know how
#to go about this!
piv = pd.pivot_table(df, index=['period', 'location'], columns = ['fuelTypeDescription'], values = ['total-consumption-btu'])

# QUESTION 1: How much electricity is being generated in the US?
# quick sums of all columns in the pivot table by types
column_sums = piv.sum()
print(column_sums)

# generation by all fuels 
US_total_generation = piv[('total-consumption-btu', 'all fuels')].sum()
print(US_total_generation)

# QUESTION 2: Where is it being generated?

# sums of each state as a table

state_generation_fuels = piv[('total-consumption-btu', 'all fuels')].groupby('location').sum()
state_generation_renewables = piv[('total-consumption-btu', 'all renewables')].groupby('location').sum()
state_total_generation = state_generation_fuels + state_generation_renewables
state_total_generation_df = pd.DataFrame({'Total Generation': state_total_generation})
print(state_total_generation_df)

# lets do the percentage of each states now so we can see which states consume the most
# I added the percentage sign too, do we like that? i can always get rid of it 

overall_total = state_total_generation.sum()
state_percentages = (state_total_generation / overall_total) * 100
state_percentages_df = pd.DataFrame({'Percentage': state_percentage})
state_percentages_df['Percentage'] = state_percentages_df['Percentage'].map('{:.2f}%'.format)
print(state_percentages_df)

# QUESTION 3: Break that down by generation type. Where are the renewable sources of power located, and how much of the overall grid are they?

# lets just start simple and do renewables first
# I took the generation of renewables at each state and then took the percentage of that to show it on the "overall grid"
all_renewables_generation = piv[('total-consumption-btu', 'all renewables')]
percentage_by_source = (all_renewables_generation / US_total_generation) * 100
renewable_breakdown_by_state = pd.DataFrame({
    'All Renewables Generation (BTU)': all_renewables_generation,
    'Percentage of Overall Grid': percentage_by_source
})

print(renewable_breakdown_by_state)

# lets test all fuels now to make sure it works

all_fuels_generation = piv[('total-consumption-btu','all fuels')]
percentage_by_source = (all_fuels_generation / US_total_generation) * 100

allfuels_breakdown = pd.DataFrame({
    'All Fuels Generation (BTU)': all_fuels_generation,
    'Percentage of Overall Grid': percentage_by_source
})

print(allfuels_breakdown)

# powerplants API

import pandas as pd
import requests
import json

api_key = 'O321szCL3xptUGbdazZYEY1HBQ5qtIT0vFev6bTe'
# url = f'https://api.eia.gov/v2/electricity/facility-fuel/data/?frequency=monthly&data[0]=total-consumption-btu&facets[state][]=AK&facets[state][]=AL&facets[state][]=AR&facets[state][]=AZ&facets[state][]=CA&facets[state][]=CO&facets[state][]=CT&facets[state][]=DC&facets[state][]=DE&facets[state][]=FL&facets[state][]=GA&facets[state][]=HI&facets[state][]=IA&facets[state][]=ID&facets[state][]=IL&facets[state][]=IN&facets[state][]=KS&facets[state][]=KY&facets[state][]=LA&facets[state][]=MA&facets[state][]=MD&facets[state][]=ME&facets[state][]=MI&facets[state][]=MN&facets[state][]=MO&facets[state][]=MS&facets[state][]=MT&facets[state][]=NC&facets[state][]=ND&facets[state][]=NE&facets[state][]=NH&facets[state][]=NJ&facets[state][]=NM&facets[state][]=NV&facets[state][]=NY&facets[state][]=OH&facets[state][]=OK&facets[state][]=OR&facets[state][]=PA&facets[state][]=PR&facets[state][]=RI&facets[state][]=SC&facets[state][]=SD&facets[state][]=TN&facets[state][]=TX&facets[state][]=UT&facets[state][]=VA&facets[state][]=VT&facets[state][]=WA&facets[state][]=WI&facets[state][]=WV&facets[state][]=WY&facets[state][]=null&start=2022-01&end=2023-12&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000&api_key={api_key}'

url = f'https://api.eia.gov/v2/electricity/facility-fuel/data/?frequency=monthly&data[0]=total-consumption-btu&start=2022-01&end=2023-12&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000&api_key={api_key}'

with requests.get(url, stream = True) as myfile:
    open("Energy", "wb").write(myfile.content)

with open("Energy", "r") as f:
    d = json.load(f)

df = pd.DataFrame(d["response"]["data"])
df

# how many power plants does each state have?

df.sort_values(by=['state', 'plantCode'], inplace=True)
power_plants_count = df.groupby('state')['plantCode'].nunique()

power_plants_count

# which powerplants generate the most?

df.drop_duplicates(subset=['plantName', 'state'], inplace=True)
df.sort_values(by='total-consumption-btu', ascending=False, inplace=True)
top_generating_powerplants = df[['plantName', 'state', 'total-consumption-btu']].head(10)

top_generating_powerplants

