import pandas as pd
import requests
import json
import seaborn as sns
import matplotlib.pyplot as plt

url = 'https://api.eia.gov/v2/electricity/electric-power-operational-data/data/?frequency=monthly&data[0]=total-consumption-btu&facets[fueltypeid][]=ALL&facets[fueltypeid][]=AOR&facets[fueltypeid][]=COW&facets[fueltypeid][]=FOS&facets[fueltypeid][]=NGO&facets[fueltypeid][]=SUN&facets[fueltypeid][]=WND&facets[sectorid][]=99&facets[location][]=AK&facets[location][]=AL&facets[location][]=AR&facets[location][]=AZ&facets[location][]=CA&facets[location][]=CO&facets[location][]=CT&facets[location][]=DC&facets[location][]=DE&facets[location][]=FL&facets[location][]=GA&facets[location][]=HI&facets[location][]=IA&facets[location][]=ID&facets[location][]=IL&facets[location][]=IN&facets[location][]=KS&facets[location][]=KY&facets[location][]=LA&facets[location][]=MA&facets[location][]=MD&facets[location][]=ME&facets[location][]=MI&facets[location][]=MN&facets[location][]=MO&facets[location][]=MS&facets[location][]=MT&facets[location][]=NC&facets[location][]=ND&facets[location][]=NE&facets[location][]=NH&facets[location][]=NJ&facets[location][]=NM&facets[location][]=NV&facets[location][]=NY&facets[location][]=OH&facets[location][]=OK&facets[location][]=OR&facets[location][]=PA&facets[location][]=PR&facets[location][]=RI&facets[location][]=SC&facets[location][]=SD&facets[location][]=TN&facets[location][]=TX&facets[location][]=US&facets[location][]=UT&facets[location][]=VA&facets[location][]=VT&facets[location][]=WA&facets[location][]=WI&facets[location][]=WV&facets[location][]=WY&start=2022-01&end=2023-01&sort[0][column]=location&sort[0][direction]=asc&offset=0&length=5000&api_key=u7e5iYnTkIJ7cwq2emALYbwgolqCG7DKuXRpaHPC'
#This downloads the json file and loads it via the json library
with requests.get(url, stream = True) as myfile:
    open("Energy", "wb").write(myfile.content)
f = open("Energy")
d = json.load(f)

df = pd.DataFrame(d["response"]["data"])
df.sort_values(by=['period', 'location', 'fueltypeid'])
piv = pd.pivot_table(df, index=['period', 'location'], columns = ['fuelTypeDescription'], values = ['total-consumption-btu'])

# QUESTION 1: How much electricity is being generated in the US?

US_total_generation = piv[('total-consumption-btu', 'all fuels')].sum()
print(US_total_generation, "btu of electricity is being generated in the United States")

# QUESTION 2: Where is it being generated?

# sums of each state 
# https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.reset_index.html 

state_total_generation = piv[('total-consumption-btu', 'all fuels')].groupby('location').sum()
state_total_generation_df = pd.DataFrame({'Total Generation': state_total_generation}).reset_index()
print(state_total_generation_df)

# sums of each state, by percentage

overall_total = state_total_generation.sum()
state_percentage = (state_total_generation / overall_total) * 100
state_percentage_df = pd.DataFrame({'Percentage': state_percentage}).reset_index()

print(state_percentage_df)

# lets make a bar graph for the percentages

sns.set(style="whitegrid")

plt.figure(figsize=(12, 6))
sns.barplot(x='location', y='Percentage', data=state_percentage_df, palette='viridis')
plt.title('Percentage Distribution of Energy Generation Across States')
plt.xlabel('State')
plt.ylabel('Percentage')
plt.xticks(rotation=90)  
plt.tight_layout()

plt.show()

# QUESTION 3: Break that down by generation type. Where are the renewable sources of power located, and how much of the overall grid are they?

# lets just start simple and do renewables first
# I took the generation of renewables at each state and then took the percentage of that to show it on the "overall grid"

all_renewables_generation = piv[('total-consumption-btu', 'all renewables')].groupby('location').sum()
percentage_by_source = (all_renewables_generation / US_total_generation) * 100
renewable_breakdown = pd.DataFrame({
    'All Renewables Generation (BTU)': all_renewables_generation,
    'Percentage of Overall Grid': percentage_by_source}).reset_index()

print("Renewable Generation Breakdown by Source:")
print(renewable_breakdown)

# now lets do it for all of them...
# i was orginally going to do it for all, which is why i did individual and not a function because it was printing weird, but then i decided to just combine them all at the end

# All fuels breakdown
all_fuels_generation = piv[('total-consumption-btu', 'all fuels')]
fuels_percentage_by_source = (all_fuels_generation / US_total_generation) * 100
fuels_breakdown = pd.DataFrame({
    'Source': 'Fuels',
    'Generation (BTU)': all_fuels_generation,
    'Percentage of Overall Grid': fuels_percentage_by_source
})

# coal breakdown
all_coal_generation = piv[('total-consumption-btu', 'all coal products')]
coal_percentage_by_source = (all_coal_generation / US_total_generation) * 100
coal_breakdown = pd.DataFrame({
    'Source': 'Coal',
    'Generation (BTU)': all_coal_generation,
    'Percentage of Overall Grid': coal_percentage_by_source
})

#fossil fuels breakdown
fossil_fuels_generation = piv[('total-consumption-btu', 'fossil fuels')]
fossil_percentage_by_source = (fossil_fuels_generation / US_total_generation) * 100
fossil_breakdown = pd.DataFrame({
    'Source': 'Fossil Fuels',
    'Generation (BTU)': fossil_fuels_generation,
    'Percentage of Overall Grid': fossil_percentage_by_source
})

#gases breakdown
gases_generation = piv[('total-consumption-btu', 'natural gas & other gases')]
gases_percentage_by_source = (gases_generation / US_total_generation) * 100
gases_breakdown = pd.DataFrame({
    'Source': 'All Gases',
    'Generation (BTU)': gases_generation,
    'Percentage of Overall Grid': gases_percentage_by_source
})

#solar breakdown
solar_generation = piv[('total-consumption-btu', 'solar')]
solar_percentage_by_source = (solar_generation / US_total_generation) * 100
solar_breakdown = pd.DataFrame({
    'Source': 'Solar',
    'Generation (BTU)': solar_generation,
    'Percentage of Overall Grid': solar_percentage_by_source
})

#wind breakdown
wind_generation = piv[('total-consumption-btu', 'wind')]
wind_percentage_by_source = (wind_generation / US_total_generation) * 100
wind_breakdown = pd.DataFrame({
    'Source': 'Wind',
    'Generation (BTU)': wind_generation,
    'Percentage of Overall Grid': wind_percentage_by_source
})

# combine them all
combined_breakdown = pd.concat([
    renewable_breakdown, fuels_breakdown, coal_breakdown,
    fossil_breakdown, gases_breakdown, solar_breakdown, wind_breakdown
])

# pivot table
pivot_table = combined_breakdown.pivot_table(
    values=['Generation (BTU)', 'Percentage of Overall Grid'],
    index='Source',
    aggfunc={'Generation (BTU)': 'sum', 'Percentage of Overall Grid': 'mean'}
)
print(pivot_table)






    