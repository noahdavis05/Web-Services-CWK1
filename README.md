# UK Lowest Cost Public Transport Options Route Finder
A RESTful API that estimates the cheapest journeys between any of the UK's 200 largest towns and cities via multiple modes of public transport.

## Table of Contents

- [UK Lowest Cost Public Transport Options Route Finder](#uk-lowest-cost-public-transport-options-route-finder)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Usage](#usage)
  - [Quick Start](#quick-start)
    - [Run Locally via Uvicorn on Linux](#run-locally-via-uvicorn-on-linux)
    - [Database](#database)
  - [API Documentation](#api-documentation)
  - [MCP](#mcp)
    - [Connecting to an AI client](#connecting-to-an-ai-client)
    - [Roo Code Example](#roo-code-example)
  - [Architecture and Design](#architecture-and-design)
    - [System Overview](#system-overview)
    - [Business Logic](#business-logic)
  - [Datasets and Sources](#datasets-and-sources)
    - [Scripts Usage](#scripts-usage)
  - [Testing](#testing)

## Features
- Find cheap public transport journeys between 200 largest UK towns and cities.
- Every UK train provider used.
- FlixBus and National Express coaches used.
- Railcard discounts included.
- Advanced Single rail fair estimation.
- MCP server.

## Usage
The quickest way to use this API is via the [SwaggerUI docs page](https://routesapi-871656980184.europe-west1.run.app/docs#). 

- Create an account using the `/auth/signup` endpoint. 
- Then log in with this account using the `/auth/login` endpoint.
- Copy the value of the bearer token returned.
- Click the authorize button at the top of the documentation, and paste in the bearer token where prompted.
- You can then freely test all `GET` endpoints.

**Note** - This will only make you a user, and therefore you will only be able to access specific enpoints (GET endpoints).  


## Quick Start
### Run Locally via Uvicorn on Linux
You can run the application with or without authentication. The authentication, if active, relies on Supabase. This is toggled through a `.env` file in the `/api` directory of the repository. This must be created yourself.

**Authenticated .env**

To run with Authentication you need a supabase account. Once you have created an account and project you can get the `SUPABASE_URL`, `SUPABASE_PUBLIC_KEY`, and `SUPABASE_SECRET_KEY`. Put them in a `.env` file like this:
```
# local sqlite3 db included in this repo
DATABASE_URL=sqlite:///./test.db

# env variables for supabase auth
SUPABASE_URL=YOUR_SUPABASE_URL
SUPABASE_PUBLIC_KEY=YOUR_PUBLISHABLE_KEY
SUPABASE_SECRET_KEY=YOUR_SECRET_KEY
AUTHENTICATION_ON=true
MCP_INTERNAL_KEY=YOUR_SECRET_MCP_KEY
```
**Without Authentication .env**
```
# local sqlite3 db included in this repo
DATABASE_URL=sqlite:///./test.db

# env variables for supabase auth
SUPABASE_URL=anything
SUPABASE_PUBLIC_KEY=anything
SUPABASE_SECRET_KEY=anything
AUTHENTICATION_ON=false
MCP_INTERNAL_KEY=YOUR_SECRET_MCP_KEY
```
**Pre-requisites** <br>
- Python version 3.12 or later.

**Follow these steps to run**
```
git clone https://github.com/noahdavis05/Web-Services-CWK1.git 
cd Web-Services-CWK1/api
## create .env file described above ##
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
uvicorn app.main:app --reload
```

### Database
Using the included sqlite3 database is recomended, but you can create and populate your own using [these commands](#Datasets). The `requirements.txt` include `psycopg2` for using a `Postgres` database, which is what the deployed API [here](https://routesapi-871656980184.europe-west1.run.app/docs#) uses.

## API Documentation
Swagger UI documentation can be found [online here](https://routesapi-871656980184.europe-west1.run.app/docs#). This documentation also allows you to test out these endpoints. This is hosted on a serverless platform so will scale to zero, and may take a while to load on first attempt.

Or PDF documentation can be found in the `/documentation` directory [here in this repo](documentation/Documentation.pdf). These docs were made through the [**rapipdf** tool](https://mrin9.github.io/RapiPdf/).

## MCP
This API supports MCP, this is only enabled for getting a journey between two cities. This allows AI assistants/tools to interact natively with the API, through natural language requests from the user. This was implemented through the `fastapi_mcp` library.
### Connecting to an AI client
**Prerequisites** - To authenticate the MCP client you must set a `MCP_INTERNAL_KEY` in your .env file. This bypasses full authentication for your MCP client as long as you set this value in the headers shown below. Or alternatively, you can manually log in using the `/auth/login` endpoint, and use this bearer token in the headers shown below.

To connect this API as a tool with an MCP client such as Claude Desktop, or Roo Code, use this configuration:
- **Transport Type** - SSE
- **URL** - Local - http://127.0.0.1:8000/mcp | Deployed - https://routesapi-871656980184.europe-west1.run.app/mcp
- **Headers** - `Authorization Bearer <token>`
### Roo Code Example
This has only been tested through the Roo Code VSCode extension. To do this, download the extension Roo Code, choose a LLM provider, and go to MCP servers tab. Here click `Edit Global MCP`, and set the `json` file it opens to this:
```
{
  "mcpServers": {
    "journey-planner": {
      "type": "sse",
      "url": "YOUR_URL",
      "headers": {
        "Authorization": "Bearer YOUR_KEY"
      }
    }
  }
}
```



## Architecture and Design
### System Overview
- The API is designed to follow RESTful practices and is built with **FastAPI**. **Pydantic** is used for validation.
- **Supabase** is used for authentication using JWT, this means we don't store any confidential information ourselves.
- **Supabase** also hosts our production Postgres database, and we interact with this through SQLAlchemy ORM.
- **Google Cloud Run** is used with deployment, and scales our code up and down with load. **Docker** is used to containerise the application for deployment, which happens on every push to the main branch.

### Business Logic
- The default database contains almost 20,000 individual routes between cities. We use a **Singleton Class** called `GraphManager` located in the `/api/utils` directory that stores these routes in a graph to avoid fetching this data on every request for a journey.
- To find a journey we use a **Dijktra's Algorithm** on our singleton class. 
- The Dijkstra's algorithm returns all the routes within the journey, and the cost breakdown including discounts from railcards, and extra transfer fees for when you use different stations in the same city as part of your route.
- We cache the results of the `find_cheapest_path` function using the `fastapi_cache` library for 1 hour. This avoids repeating the same calculations numerous times.


## Datasets and Sources
To work out the cheapest route between the UK's 200 largest cities and towns I used all trainlines, national express coaches, and flixbus coaches. Information on the data for these can be found below.
1. **Trains** - I used the National Rail Data Portal. I made a free account and gained access to the train fares dataset. This provides you with all rail fares between any two stations. This only includes standard ticket prices, not tickets such as advanced singles which are based on demand and not available to the public. 

    It wasn't possible to map stations to city via strings, as many city or station names include the names of other cities or stations. For example the city Chester would also be included in Winchester and Manchester. Therefore, I used the governments **NaPTAN** dataset which maps all UK train stations to the city they are in, and their **ATCO code**. I then used a **RailReferences** dataset which maps ATCO codes, CRS codes, and station names. The original fares dataset uses the CRS codes allowing me to accurately map all rail stations within my 200 cities and towns without any errors.
   
   My code to extract this can be found in `/datasets/train-fares`. This includes code to get the train prices between all 200 chosen cities into CSV format, and code to upload this to my database through my API.

    | Dataset | Link | Notes |
    | ------- | ---- | ----- |
    | Fares Dataset | https://opendata.nationalrail.co.uk/feeds https://wiki.openraildata.com/index.php/Fares_Data | National Rail Liscence (Had to apply for access to use in a University project) |
    | NaPTAN Dataset | https://www.data.gov.uk/dataset/ff93ffc1-6656-47d8-9155-85ea0b8f2251/naptan | Open Government Licence |
    | RailReferences | https://gist.github.com/crablab/93a50eeb338646614287eddc3c2776b1 | From Github user crablab, which has modified the NaPTAN dataset under same licence |
   
2. **National Express Coaches** - I used the governments Bus Open Data Service. This contains all bus and coach routes across the country and fares for them. From the government website I just downloaded the National Express fares data. This data is in XML more specifically NeTeX which is a standard across UK bus service providers. This dataset contains around 70 coach routes with pricing. It is worth noting, this dataset doesn't contain fares for all National Express routes as many routes are done through dynamic pricing. My code to extract the data from the dataset and upload it to my database can be found in `/datasets/coach-fares/national-express`.

    | Dataset | Link | Notes |
    | ------- | ---- | ----- |
    | National Express BODS | https://data.bus-data.dft.gov.uk/fares/dataset/20653/ | Open Government Licence | 

3. **Flixbus Coaches** - Flixbus unfortunately doesn't upload their fares to the Bus Open Data Service. Therefore to get prices, I used their api to get typical prices for services between cities weeks in advance to get standard prices. This code can be found in `datasets/coach-fares/flix-bus`. To ensure I used their API as minimally as possible I used their timetable dataset to ensure I worked out every direct Flix Bus route between the 200 UK towns and cities I chose, and only queried these routes.

    | Data Source | Link | Notes |
    | ----------- | ---- | ----- |
    | Flix Bus Routes | https://data.bus-data.dft.gov.uk/coach/download | Open Government Licence |
    | Internal Website API | | Used the API found in the network tab on their website. I ensured minimal queries with delays inbetween. |


4. **UK-Cities** - This was a dataset containing all cities and towns in the UK with their given co-ordinates, and populations. I used this to extract the 200 most populated cities and towns to use in this project.

    | Data Source | Link | Notes |
    | ----------- | ---- | ----- |
    | Simple maps UK cities | https://simplemaps.com/data/uk-cities | Creative Commons Attribution 4.0 | 


### Scripts Usage
Within the `/datasets` dir you can find the scripts to populate the database through the API. 

**Pre-requisites**

- Ensure the API is running [(See above)](#quick-start). 
- Use the authorization endpoints to get a bearer token and add this to all requests. Ensure you use an admin account.
- Go to the `/docs` or use a tool such as postman to make 2 post queries to create transport modes. Firstly create 'coach', and secondly create 'train'.
```
cd /datasets
source venv/bin/activate
cd uk-cities
python3 get_cities.py
cd /../train-fares
python3 upload_routes.py
cd /../coach-fares/flix-bus
python3 upload_routes.py
cd /../national_express
python3 extract_fares.py
```

## Testing 
Tests for the api can be found in `/api/testing`. These tests use the `pytest` library. Services such as authentication and database session are mocked in the `conftest.py` file. Where a database is needed for this, these tests use the `test.db` database in this directory. 

The database is required to always remain the same in order for these tests to always work correctly. For example, if we are testing a **DELETE** route, we need the item deleted to be put back into the database. The mock database session ensures that once a test has ran all database changes are rolled back.

Tests are ran automatically on commit through github actions in the `/.github/workflows/tests.yaml` file. But can also be ran manually. To run manually, create a `.env.test` file in the `/api` directory which looks like:

```

# Local Development
DATABASE_URL=sqlite:///./testing/test.db

# Keys for supabase auth
SUPABASE_URL=ANY_WEBSITE_URL
SUPABASE_PUBLIC_KEY=temp
SUPABASE_SECRET_KEY=temp
AUTHENTICATION_ON=true
MCP_INTERNAL_KEY=YOUR_SECRET_MCP_KEY
```

Then run the following commands to run the tests:
```
cd /api
source venv/bin/activate
pytest
```

