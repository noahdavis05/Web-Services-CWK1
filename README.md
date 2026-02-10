# UK Lowest Cost Public Transport Options
## Overview
This API finds the estimated cheapest route between any of the top 200 largest UK towns and cities via public transport. This public transport includes UK trains from all providers, and UK coaches through National Express, and Flixbus.

## Usage
### Run API 
**For Development using Uvicorn**
1. Navigate to the `api` directory. `cd api`
2. Set up Python virtual environment. `python3 -m venv venv`.
3. Activate Python virtual environment. `source venv/bin/activate`.
4. Install dependencies. `pip3 install -r requirements.txt`.
5. Create a `.env` file in the `api` directory. Add the line `DATABASE_URL=sqlite:///./test.db` to use a local SQL database. Or can use the Supabase SQL connection string to the deployment database.
6. If the database doesn't exist/tables don't exist. Run `alembic upgrade head`.
7. Run FastAPI application via uvicorn. `uvicorn app.main:app --reload`

### Datasets
1. Set the correct `DATABASE_URL` in the .env in the `api` directory.
2. Run the API - See above.
3. Go to the URL `127.0.0.1:8000/docs#/`. 
4. Find the **Travel Routes** section and test the **POST** endpoint. Create firstly a travel method 'coach' and secondly a travel method 'train'.
5. Open a new terminal and navigate to `/datasets/uk-cities`.
6. Activate venv `source venv/bin/activate`.
7. Run the script get_cities.py `python3 get_cities.py`. This will add all cities to the database.
8. Deactivate the venv `deactivate`, and navigate to `datasets/train-fares`.
9. Activate the venv, and run the script `upload_routes.py`. `python3 upload_routes.py`.
10. Deactivate the venv, and navigate to `datasets/coach-fares/flix-bus/`.
11. Activate the venv, and run script `upload_routes.py`. `python3 upload_routes.py`.
12. Deactivate the venv and navigate to `/datasets/coach-fares/national-express`.
13. Activate the venv and run the script `extract_fares.py`. `python3 extract_fares.py`.


## Datasets
To work out the cheapest route between the UK's 200 largest cities and towns I used all trainlines, national express coaches, and flixbus coaches. Information on the data for these can be found below.
1. **Trains** - I used the National Rail Data Portal. I made a free account and gained access to the train fares dataset. This provides you with all rail fares between any two stations. This only includes standard ticket prices, not tickets such as advanced singles which are based on demand and not available to the public. My code to extract this can be found in `/datasets/train-fares`. This includes code to get the train prices between all 200 chosen cities into CSV format, and code to upload this to my database through my API.
2. **National Express Coaches** - I used the governments Bus Open Data Service. This contains all bus and coach routes across the country and fares for them. From the government website I just downloaded the National Express fares data. This data is in XML more specifically NeTeX which is a standard across UK bus service providers. This dataset contains around 70 coach routes with pricing. It is worth noting, this dataset doesn't contain fares for all National Express routes as many routes are done through dynamic pricing. My code to extract the data from the dataset and upload it to my database can be found in `/datasets/coach-fares/national-express`.
3. **Flixbus Coaches** - Flixbus unfortunately doesn't upload their fares to the Bus Open Data Service. Therefore to get prices, I used their api to get typical prices for services between cities weeks in advance to get standard prices. This code can be found in `datasets/coach-fares/flix-bus`.
4. **UK-Cities** - This was a dataset containing all cities and towns in the UK with their given co-ordinates, and populations. I used this to extract the 200 most populated cities and towns to use in this project.

**Give proper links and references to all**

