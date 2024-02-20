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

state_generation_fuels = piv[('total-consumption-btu', 'all fuels')].groupby('location').sum()
state_generation_renewables = piv[('total-consumption-btu', 'all renewables')].groupby('location').sum()
state_total_generation = state_generation_fuels + state_generation_renewables
print(state_total_generation)

# QUESTION 3: Break that down by generation type. Where are the renewable sources of power located, and how much of the overall grid are they?

all_renewables_generation = piv[('total-consumption-btu', 'all renewables')]
percentage_by_source = (all_renewables_generation / US_total_generation) * 100
renewable_breakdown_by_state = pd.DataFrame({
    'All Renewables Generation (BTU)': all_renewables_generation,
    'Percentage of Overall Grid': percentage_by_source
})

print(renewable_breakdown_by_state)
