\# ⚡ EV Charging Station Location Planner



\### Plan Smarter. Charge Better.



A worldwide geospatial planning platform designed to identify, analyze and recommend promising locations for new electric vehicle charging stations using real-world geographical data, interactive maps and intelligent suitability scoring.



\## 🌍 Project Overview



The EV Charging Station Location Planner helps charging companies, city planners, business owners and researchers make informed decisions about EV charging infrastructure expansion.



The platform evaluates candidate locations based on existing charging infrastructure, nearby commercial facilities and road proximity to provide meaningful location suitability recommendations.



\## 🎯 Project Objectives



\- Identify potential gaps in existing EV charging infrastructure.

\- Evaluate candidate locations using real-world geographical data.

\- Generate location suitability scores ranging from 0 to 100.

\- Compare multiple locations and recommend promising candidates.

\- Support worldwide location exploration.

\- Enable data-driven infrastructure planning.



\## ✨ Key Features



| Feature | Description |

|---|---|

| User Authentication | Secure registration and login using JWT authentication |

| Personalized Dashboard | User-specific planning interface |

| Interactive Map | Explore worldwide locations and reported charging stations |

| Location Search | Search cities, areas and addresses |

| Custom Candidate Selection | Select a location directly on the map |

| Nearby EV Stations | Discover reported charging infrastructure |

| Site Analysis | Generate suitability scores and meaningful planning insights |

| Site Comparison | Compare up to four candidate locations |

| Saved Locations | Shortlist promising locations for future analysis |

| User Preferences | Customize suitability scoring weights |

| Profile Management | View and update personal information |

| Password Management | Securely change account passwords |

| Admin Panel | Authorized management of charging station records |



\## 🛠️ Technology Stack



| Layer | Technologies |

|---|---|

| Frontend | React.js, JavaScript, HTML, CSS, Vite |

| Interactive Maps | Leaflet, OpenStreetMap |

| Backend | Python, FastAPI |

| Database | PostgreSQL, Supabase |

| Geospatial Extension | PostGIS |

| Database Connectivity | Psycopg |

| Authentication | JWT, Argon2 password hashing |

| Data Processing | Pandas, Python |

| API Testing | Swagger UI |

| Version Control | Git, GitHub |

| Development Environment | Visual Studio Code |



\## 🏗️ System Architecture



```mermaid

flowchart TD

&#x20;   A\[User / Administrator] --> B\[React Frontend]

&#x20;   B --> C\[FastAPI REST API]

&#x20;   C --> D\[Authentication and Profile Management]

&#x20;   C --> E\[Location Search and Map Services]

&#x20;   C --> F\[Suitability Scoring Engine]

&#x20;   C --> G\[Site Comparison and Preferences]

&#x20;   C --> H\[Admin Management]

&#x20;   D --> I\[(Supabase PostgreSQL)]

&#x20;   G --> I

&#x20;   H --> I

&#x20;   E --> J\[Mapbox]

&#x20;   F --> K\[Open Charge Map]

&#x20;   F --> L\[Geoapify]

&#x20;   F --> M\[TomTom]

```



\## 📊 Location Suitability Scoring



The system uses a weighted scoring approach to evaluate candidate locations.



| Scoring Factor | Default Weight |

|---|---:|

| Charging Coverage Gap | 40% |

| Commercial Facilities | 35% |

| Road Proximity | 25% |

| Total | 100% |



\### Scoring Formula



```

Suitability Score =

&#x20;   (Coverage Gap Score × 0.40)

&#x20; + (Commercial Facilities Score × 0.35)

&#x20; + (Road Proximity Score × 0.25)

```



Users can customize scoring weights through the Preferences page.



\### Suitability Classification



| Score | Classification |

|---|---|

| 80–100 | High Suitability |

| 60–79.99 | Moderate Suitability |

| 40–59.99 | Low Suitability |

| Below 40 | Very Low Suitability |

| Missing required information | Insufficient Data |



The system provides planning insights based on available geographical information and identifies promising candidates for further feasibility assessment.



\## 🔌 External API Integrations



| Service | Purpose |

|---|---|

| Open Charge Map | Reported EV charging station information |

| Mapbox | Worldwide location search and reverse geocoding |

| Geoapify | Nearby commercial facilities and infrastructure |

| TomTom | Road segment and traffic information |

| OpenStreetMap | Interactive geographical map display |



\## 🗄️ Database Design



The application uses Supabase PostgreSQL for persistent data storage.



| Table | Purpose |

|---|---|

| planner\_users | User accounts, roles and profile information |

| planner\_shortlist | Saved candidate locations |

| planner\_preferences | User-specific planning preferences |

| planner\_stations | Administrator-managed station records |



Passwords are stored as secure hashes rather than plaintext.



\## 📁 Project Structure



```

EV-Charging-Station-Location-Planner/

│

├── backend/

│   ├── app/

│   │   ├── routers/

│   │   ├── schemas/

│   │   ├── services/

│   │   ├── database.py

│   │   └── main.py

│   ├── scripts/

│   ├── .env.example

│   ├── requirements.txt

│   ├── setup\_database.sql

│   └── upgrade\_v2.sql

│

├── frontend/

│   ├── public/

│   ├── src/

│   │   ├── assets/

│   │   ├── components/

│   │   ├── pages/

│   │   ├── services/

│   │   ├── App.jsx

│   │   └── App.css

│   ├── package.json

│   └── vite.config.js

│

├── .gitignore

└── README.md

```



\## 🚀 Installation and Setup



\### 1. Clone the Repository



```bash

git clone https://github.com/TanviGanji18/EV-Charging-Station-Location-Planner.git



cd EV-Charging-Station-Location-Planner

```



\### 2. Backend Setup



```powershell

cd backend



python -m venv venv



.\\venv\\Scripts\\Activate.ps1



pip install -r requirements.txt

```



\### 3. Environment Configuration



Create a `.env` file inside the backend directory using `.env.example` as a reference.



```env

OPEN\_CHARGE\_MAP\_API\_KEY=

MAPBOX\_ACCESS\_TOKEN=

GEOAPIFY\_API\_KEY=

TOMTOM\_API\_KEY=



DB\_HOST=

DB\_PORT=5432

DB\_NAME=postgres

DB\_USER=

DB\_PASSWORD=



JWT\_SECRET\_KEY=

```



Configure valid API credentials and database connection details.



Never commit the actual `.env` file to GitHub.



\### 4. Database Setup



\- Create or configure a Supabase PostgreSQL project.

\- Enable the PostGIS extension.

\- Execute `setup\_database.sql` using the Supabase SQL Editor.

\- For an existing older database, execute `upgrade\_v2.sql` to add the updated profile fields.



\### 5. Run the Backend



```bash

uvicorn app.main:app --reload

```



Backend URL: http://127.0.0.1:8000



Swagger API Documentation: http://127.0.0.1:8000/docs



\### 6. Frontend Setup



Open a separate terminal from the project root.



```bash

cd frontend



npm install



npm run dev

```



Open the local URL displayed by Vite.



\## 🔗 Main API Endpoints



| Method | Endpoint | Description |

|---|---|---|

| POST | /api/v1/auth/register | Register user |

| POST | /api/v1/auth/login | Authenticate user |

| GET | /api/v1/auth/me | Retrieve account information |

| GET | /api/v1/locations/search | Search worldwide locations |

| GET | /api/v1/locations/reverse | Reverse geocoding |

| GET | /api/v1/stations/nearby | Retrieve nearby charging stations |

| GET | /api/v1/infrastructure/nearby | Retrieve nearby infrastructure |

| GET | /api/v1/infrastructure/summary | Infrastructure summary |

| GET | /api/v1/traffic | Road and traffic information |

| POST | /api/v1/analysis | Analyze candidate location |

| POST | /api/v1/compare | Compare candidate locations |

| GET | /api/v1/shortlist | Retrieve saved locations |

| POST | /api/v1/shortlist | Save a location |

| DELETE | /api/v1/shortlist/{id} | Remove saved location |

| GET | /api/v1/preferences | Retrieve preferences |

| PUT | /api/v1/preferences | Update preferences |

| GET | /api/v1/admin/stations | Retrieve managed stations |

| POST | /api/v1/admin/stations | Add station |

| PUT | /api/v1/admin/stations/{id} | Update station |

| DELETE | /api/v1/admin/stations/{id} | Delete station |



Refer to Swagger UI for the complete API documentation, including profile management operations.



\## 🔐 Security Features



\- JWT-based authentication

\- Secure password hashing

\- Role-based access control

\- Administrator-only station management

\- Input validation

\- Environment-based credential management

\- Protected user-specific records



\## 🧪 Testing



Development testing covers:



\- User registration and authentication

\- Database connectivity

\- Worldwide location search

\- External API integration

\- Charging station retrieval

\- Infrastructure analysis

\- Location suitability scoring

\- Site comparison

\- Saved location management

\- User preferences

\- Administrator authorization and CRUD operations



Independent integration testing and deployed application verification are part of the final release process.



\## 📸 Application Screens



\- Landing Page

\- Sign Up

\- Login

\- Dashboard

\- Explore Map

\- Site Analysis

\- Compare Sites

\- Saved Locations

\- Preferences

\- My Profile

\- Admin Panel



Application screenshots will be added to the repository.



\## 👥 Team 18



\*\*Anurag University — B.Tech Project\*\*



| Team Member | Responsibility |

|---|---|

| Ganji Tanvi | Backend Development, Database and Frontend Integration |

| Nikitha G | Frontend Development and UI/UX |

| Akash B | Software Testing and Quality Assurance |

| Nehal Maria Choudhary Dhaka | Application Deployment |



\## 🌐 Deployment



Deployment link: To be updated after deployment.



\## ⚠️ Current Limitations



\- Results depend on external API availability and geographical data coverage.

\- Charging station information represents reported infrastructure, not guaranteed live availability.

\- Suitability scores are heuristic planning indicators, not validated investment feasibility assessments.

\- Analysis response times depend on external service performance.

\- Charger type is currently stored as a user preference.

\- Administrator-managed station records are maintained separately from external provider results.



\## 🔮 Future Enhancements



\- Machine learning-based charging demand forecasting

\- Automatic candidate location generation

\- Electrical grid capacity assessment

\- Installation cost estimation

\- Land availability analysis

\- Advanced geographical heatmaps

\- Improved caching and response times

\- Integration of administrator-managed stations into suitability analysis



\---



\*\*EV Charging Station Location Planner — Building a smarter and more sustainable electric mobility future.\*\*

