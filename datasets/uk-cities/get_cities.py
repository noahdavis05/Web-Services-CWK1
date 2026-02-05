import pandas as pd

cities_df = pd.read_csv("data/ukcities.csv")

CITIES = 200
# get 200 largest cities
largest_cities = cities_df.nlargest(CITIES,['population'])

# now add our cities into an array of dictionaries - We can then use our API to add these to database
# each dict will contain city name, latitude, longitude
cities = []

for row in largest_cities.itertuples():
    # Welsh cities are in Welsh, but admin_name is in English
    # All other datasets use the English names, therefore must use english names
    if row.country_name == "Wales":
        name = row.admin_name
    else:
        name = row.city
    
    cities.append(
        {
            "name":name,
            "latitude":row.lat,
            "longitude":row.lng
        }
    )

print(cities)

