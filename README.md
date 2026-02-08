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

