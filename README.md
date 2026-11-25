\# EV Charging Station Location Planner



\## Project Overview



A worldwide geospatial planning application designed to identify and evaluate suitable locations for installing new electric vehicle charging stations using existing charging infrastructure, commercial facilities and road proximity information.



\## Team 18 — Anurag University



\## Backend Features



\- Worldwide EV charging station discovery

\- Location search and reverse geocoding

\- Nearby commercial infrastructure discovery

\- Traffic and road information analysis

\- Location suitability scoring out of 100

\- Comparison of up to four candidate locations

\- User registration and login

\- JWT-based authentication

\- Role-based admin authorization

\- Saved locations and shortlist management

\- User preference storage

\- Admin station management



\## Technology Stack



| Component | Technology |

|---|---|

| Programming Language | Python |

| Backend Framework | FastAPI |

| Database | PostgreSQL |

| Database Hosting | Supabase |

| Geospatial Extension | PostGIS |

| Authentication | JWT and Argon2 |

| API Documentation | Swagger UI |

| Version Control | Git and GitHub |

| Frontend (planned integration) | React.js |



\## External API Integrations



| API | Purpose |

|---|---|

| Open Charge Map | Existing EV charging stations |

| Mapbox | Location search and reverse geocoding |

| Geoapify | Nearby infrastructure and commercial facilities |

| TomTom | Traffic and road segment information |



\## Suitability Scoring



The current scoring engine uses three weighted factors:



| Factor | Weight |

|---|---:|

| Charging station coverage gap | 40% |

| Nearby commercial facilities | 35% |

| Road proximity | 25% |



Final Score = (Coverage Gap × 0.40) + (Commercial Facilities × 0.35) + (Road Proximity × 0.25)



The scoring system is a provisional planning heuristic, not a validated investment feasibility model.



\## Database Tables



\- planner\_users

\- planner\_shortlist

\- planner\_preferences

\- planner\_stations



\## Project Structure



```text

EV-Charging-Station-Location-Planner/

├── backend/

│   ├── app/

│   │   ├── routers/

│   │   ├── schemas/

│   │   ├── services/

│   │   ├── database.py

│   │   └── main.py

│   ├── scripts/

│   ├── .env.example

│   ├── .gitignore

│   ├── requirements.txt

│   └── setup\_database.sql

├── .gitignore

└── README.md

```



\## Installation and Setup



\### 1. Navigate to the backend



```bash

cd backend

```



\### 2. Create a virtual environment



```bash

python -m venv venv

```



\### 3. Activate the environment on Windows



```powershell

.\\venv\\Scripts\\Activate.ps1

```



\### 4. Install dependencies



```bash

pip install -r requirements.txt

```



\### 5. Configure environment variables



Create a `.env` file using `.env.example` as a template and provide valid external API credentials, PostgreSQL connection details and a secure JWT secret.



Never commit actual credentials to GitHub.



\### 6. Configure the database



Create a PostgreSQL database, enable PostGIS and execute `setup\_database.sql`.



\### 7. Start the backend



```bash

uvicorn app.main:app --reload

```



\### 8. Access API documentation



\- Backend: http://127.0.0.1:8000

\- Swagger UI: http://127.0.0.1:8000/docs

\- Health Check: http://127.0.0.1:8000/health



\## API Endpoints



| Method | Endpoint | Description |

|---|---|---|

| GET | / | Backend information |

| GET | /health | Health check |

| GET | /api/v1/stations/nearby | Nearby EV stations |

| GET | /api/v1/locations/search | Location search |

| GET | /api/v1/locations/reverse | Reverse geocoding |

| GET | /api/v1/infrastructure/categories | Infrastructure categories |

| GET | /api/v1/infrastructure/nearby | Nearby facilities |

| GET | /api/v1/infrastructure/summary | Infrastructure summary |

| GET | /api/v1/traffic | Traffic information |

| POST | /api/v1/analysis | Suitability analysis |

| POST | /api/v1/compare | Site comparison |

| POST | /api/v1/auth/register | User registration |

| POST | /api/v1/auth/login | User login |

| GET | /api/v1/auth/me | Current user |

| GET | /api/v1/shortlist | Retrieve saved locations |

| POST | /api/v1/shortlist | Save location |

| DELETE | /api/v1/shortlist/{id} | Remove saved location |

| GET | /api/v1/preferences | Retrieve preferences |

| PUT | /api/v1/preferences | Update preferences |

| GET | /api/v1/admin/stations | Retrieve managed stations |

| POST | /api/v1/admin/stations | Add station |

| PUT | /api/v1/admin/stations/{id} | Update station |

| DELETE | /api/v1/admin/stations/{id} | Delete station |



\## Sample Site Comparison



| Location | Suitability Score | Classification |

|---|---:|---|

| Hyderabad, India | 95.46 | High |

| London, United Kingdom | 53.41 | Low |



These results represent specific tested coordinates and provider data at the time of testing, not entire cities.



\## Testing



Core backend operations have been manually tested using Swagger UI, including:



\- External API integrations

\- Location analysis and comparison

\- User registration and login

\- JWT authentication

\- Shortlist operations

\- Preference updates

\- Admin CRUD operations

\- Unauthorized access rejection



\## Current Limitations and Future Enhancements



\- User preference weights are not yet integrated into suitability calculations.

\- Charger-type filtering requires further integration.

\- Admin-managed stations are stored separately from external station results.

\- PostGIS spatial query integration is pending.

\- Automatic candidate location generation is pending.

\- Response time optimization is required.

\- External provider coverage may be incomplete.

\- Frontend integration and deployment are pending.



\## Data Attribution



External data is provided by Open Charge Map, Mapbox, Geoapify, OpenStreetMap contributors and TomTom, subject to their respective licensing and usage terms.



\## Project Status



Core backend implemented and manually tested. Ready for further frontend integration, testing and deployment.

