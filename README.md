# UELE Server

Backend API for a fantasy sports platform (leagues, contestants, lineups, matchups and player data).

**Tech stack:**
- Python, FastAPI
- MongoDB (motor / pymongo) with Beanie document models
- Authentication: fastapi-users (Beanie backend) with database-backed access tokens

**Requirements:**
- See `requirements.txt` for exact versions. Key packages include `fastapi`, `uvicorn`, `motor`, `beanie`, `fastapi-users`, and `python-dotenv`.

**Environment**
- Create a `.env` file or set environment variables. The app expects at least:
	- `MONGODB_URI` — MongoDB connection string used by Motor (connected in `main.py`).

**Run (development):**
```bash
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The application uses an async lifespan to initialize a Motor client and Beanie models (see `main.py`).

CORS origins are configured in `main.py` (local dev and a deployed client URL).

API Overview
- Authentication:
	- Uses `fastapi-users` with Beanie models. Routes are mounted under `/auth` and user routes under `/users` (see `auth/routers.py`).
	- Token auth uses a database-backed Bearer transport (`auth/users.py`).

- League endpoints (`routers/league_router.py`):
	- `POST /league/` — create a new league (commissioner is set to the authenticated user)
	- `GET /league/{id}` — fetch league
	- `GET /league/schedule/{id}` — league matchups
	- `GET /league/available/{user_id}` — leagues available for a user to join
	- `PUT /league/{id}` — update league (commissioner only)
	- `DELETE /league/{id}` — delete league (commissioner only)

- Contestant endpoints (`routers/contestant_router.py`):
	- `POST /contestant/{league_id}` — join a league as a contestant
	- `GET /contestant/{id}` — fetch contestant
	- `GET /contestant/user/{user_id}` — contestants for a user (with league info)
	- `GET /contestant/league/{league_id}` — contestants in a league
	- `PUT /contestant/{id}` — update contestant (owner only)
	- `DELETE /contestant/{id}` — delete contestant (owner only)

- Lineup endpoints (`routers/lineup_router.py`):
	- `POST /lineup/{contestant_id}` — create lineup for contestant
	- `GET /lineup/{id}` — fetch a lineup
	- `GET /lineup/league/{league_id}` — all lineups for a league
	- `GET /lineup/contestant/{contestant_id}` — lineup for a contestant and week
	- `PUT /lineup/{id}` — update lineup selections (with locking, availability and team-count logic)

- Matchup endpoints (`routers/matchup_router.py`):
	- `GET /matchup/{id}` — get matchup with joined lineup data for both teams

- Data endpoints (`routers/data_router.py`):
	- `GET /players/mlb/{contestant_id}` — search MLB players (filters: position, team, sort)
	- `GET /players/nfl/{contestant_id}` — search NFL players (filters: position, team, sort)
	- `GET /teams/nfl/` — list NFL teams

Models and Schemas
- Models for `LeagueModel`, `LineupModel`, `PlayerModel`, and contestant/matchup models live under `models/` (pydantic/Beanie style).
- Authentication models and Beanie user/access-token documents are in `auth/`.

Notes & Next steps
- Ensure `MONGODB_URI` is correctly set before starting the server.
- The app mounts routers in `main.py` and exposes an example protected route `/authenticated-route`.
- If you want, I can:
	- Add example curl/Postman requests for main flows,
	- Generate OpenAPI/Swagger usage notes, or
	- Expand the README with deployment instructions (Heroku/containers).

License
- See `LICENSE` in repository root.
