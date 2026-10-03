# SmartRoad AI 🚧

### Intelligent Road Construction Planning System

SmartRoad AI is a web-based road construction planning backend designed to help governments and infrastructure planners connect villages while minimizing overall road construction cost.

The system models villages as **vertices** and candidate roads as **weighted edges** in a graph. It uses **Kruskal's Minimum Spanning Tree (MST)** algorithm with **Union-Find / Disjoint Set Union (DSU)** to select a cost-efficient set of roads that connects all villages without creating unnecessary cycles.

The backend also supports secure JWT authentication, project saving, MongoDB persistence, scenario-based planning, budget analysis, risk indicators, environmental estimates, and automatic API documentation through Swagger UI.

---

## 🎯 Problem Statement

A government wants to connect several villages with roads. The construction cost of each possible road is different. Every village must be connected to the road network while keeping the total construction cost as low as possible.

For a network represented as a weighted graph, the required solution is a **Minimum Spanning Tree**: a set of roads that connects all villages with no cycles and minimum total selected cost, provided the input graph is connected under the applicable constraints.

### Why SmartRoad AI?

- Reduces unnecessary road construction.
- Helps compare candidate roads based on cost and constraints.
- Automatically avoids cyclic road connections.
- Provides budget and infrastructure indicators.
- Gives explanations for selected and rejected roads.
- Provides a reusable API that can be connected to a web dashboard.

---

## ✨ Key Features

### 🛣️ Intelligent Road Planning

- Kruskal's Minimum Spanning Tree algorithm.
- Union-Find / DSU with path compression and union by rank.
- Road ranking based on effective construction cost.
- Cycle detection and rejection.
- Connectivity verification.

### 🌦️ Scenario Analysis

Each road can include:

- Construction cost in ₹ lakh.
- Road quality score.
- Flood-risk percentage.
- Maintenance cost.
- Road length in kilometres.

The scenario can also include:

- Overall budget.
- Construction cost multiplier.
- Weather severity.
- Minimum acceptable road quality.

Weather severity can increase the effective cost of flood-prone roads, allowing the planning result to respond to scenario conditions.

### 📊 Planning Insights

The API returns:

- Selected roads.
- Rejected roads and reasons.
- Total effective construction cost.
- Estimated money saved.
- Remaining budget or budget shortage.
- Average flood-risk score.
- Total road length.
- Estimated trees removed.
- Estimated CO₂ impact.
- Suggested saplings to plant.
- Green score.
- Algorithm runtime.

### 🔐 Authentication

- JWT bearer-token authentication.
- Password hashing using bcrypt.
- Protected planning and project APIs.
- Token expiration after a configured period.

### 💾 Project Management

Authenticated users can:

- Save planning scenarios.
- List their saved projects.
- Load an individual project.
- Delete a project.

MongoDB is used when `MONGO_URI` is configured; otherwise, the application can use an in-memory store for local development.

### 📚 API Documentation

FastAPI automatically provides interactive documentation through:

- Swagger UI: `/docs`
- ReDoc: `/redoc`

---

## 🏗️ System Architecture

```text
                         ┌─────────────────────┐
                         │       User          │
                         │  Web Dashboard/UI   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   JWT Authentication│
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    FastAPI Backend   │
                         │     REST APIs        │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
          ┌──────────────────┐            ┌──────────────────┐
          │ Road Planning    │            │ Project Manager  │
          │ Engine           │            │                  │
          └────────┬─────────┘            └────────┬─────────┘
                   │                               │
                   ▼                               ▼
          ┌──────────────────┐            ┌──────────────────┐
          │ Kruskal MST      │            │ MongoDB          │
          │ + Union-Find     │            │ Project Storage  │
          └────────┬─────────┘            └──────────────────┘
                   │
                   ▼
          ┌──────────────────┐
          │ Optimized Road   │
          │ Network +        │
          │ Planning Metrics │
          └──────────────────┘
```

---

## 🧠 How the Algorithm Works

SmartRoad AI uses **Kruskal's Algorithm** to construct a Minimum Spanning Tree.

### Step 1 — Validate the Input

The backend verifies that each road refers to valid villages and does not connect a village to itself.

### Step 2 — Calculate Effective Cost

The system starts with the base road cost and adjusts it using the scenario's cost multiplier and weather/flood-risk conditions.

### Step 3 — Sort Roads

Candidate roads are sorted from lowest to highest effective cost.

### Step 4 — Select Roads

Kruskal's algorithm considers roads in sorted order and adds a road when it connects two previously separate components.

### Step 5 — Avoid Cycles

The DSU/Union-Find structure detects whether adding a road would create a cycle. Cyclic roads are rejected.

### Step 6 — Generate the Plan

The selected roads form the optimized network. The backend then calculates cost, budget, risk, environmental and runtime metrics.

### Complexity

For `E` candidate roads, the dominant sorting step gives approximately:

**Time Complexity: O(E log E)**

Union-Find operations are near-constant amortized time with path compression and union by rank.

---

## 🧰 Technology Stack

| Layer                | Technology                 |
| -------------------- | -------------------------- |
| Programming Language | Python 3.12                |
| API Framework        | FastAPI                    |
| Data Validation      | Pydantic                   |
| Algorithm            | Kruskal's MST              |
| Graph Structure      | Union-Find / DSU           |
| Authentication       | JWT + OAuth2 Password Flow |
| Password Hashing     | bcrypt                     |
| Database             | MongoDB 7                  |
| MongoDB Driver       | Motor                      |
| Server               | Uvicorn                    |
| Containerization     | Docker                     |
| Orchestration        | Docker Compose             |
| API Documentation    | Swagger UI / ReDoc         |

---

## 📁 Project Structure

```text
SmartRoad-AI/
│
├── main.py              # FastAPI application, authentication,
│                        # MST engine and project APIs
│
├── requirements.txt     # Python dependencies
│
├── Dockerfile           # Backend container configuration
│
├── docker-compose.yml   # FastAPI + MongoDB services
│
└── README.md            # Project documentation
```

> The supplied ZIP contains the backend and deployment configuration. A separate frontend/dashboard can consume the REST APIs exposed by this backend.

---

## 🚀 Getting Started

### Prerequisites

Install:

- Python 3.12+
- pip
- Git

For Docker deployment:

- Docker
- Docker Compose

---

## 💻 Run Locally

### 1. Clone the repository

```bash
git clone <YOUR-GITHUB-REPOSITORY-URL>
cd SmartRoad-AI
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set environment variables

Windows PowerShell:

```powershell
$env:SECRET_KEY="replace-with-a-long-random-secret"
```

Optional MongoDB configuration:

```powershell
$env:MONGO_URI="mongodb://localhost:27017"
```

Optional CORS configuration:

```powershell
$env:CORS_ORIGINS="*"
```

### 5. Start the API

```bash
uvicorn main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

Open API documentation at:

```text
http://localhost:8000/docs
```

---

## 🐳 Run with Docker Compose

The project includes Docker configuration for FastAPI and MongoDB.

### 1. Set the secret key

Linux/macOS:

```bash
export SECRET_KEY="replace-with-a-long-random-secret"
```

Windows PowerShell:

```powershell
$env:SECRET_KEY="replace-with-a-long-random-secret"
```

### 2. Start the services

```bash
docker compose up --build
```

This starts:

- FastAPI API on port `8000`
- MongoDB on the internal Docker network

Open:

```text
http://localhost:8000/docs
```

To stop the services:

```bash
docker compose down
```

MongoDB data is persisted through the `mongo_data` Docker volume.

---

## 🔑 Demo Authentication

The current prototype defines demo users in the backend for development/testing:

| Username  | Password       |
| --------- | -------------- |
| `officer` | `smartroad123` |
| `admin`   | `admin@123`    |

> **Security:** These credentials are for the supplied prototype only. Replace the demo-user approach with database-backed credentials and secure secret management before production deployment.

---

## 🔌 API Endpoints

### Authentication

| Method | Endpoint          | Description                 |
| ------ | ----------------- | --------------------------- |
| POST   | `/api/auth/login` | Login and receive JWT token |
| GET    | `/api/auth/me`    | Get authenticated user      |

### Road Planning

| Method | Endpoint   | Description                  |
| ------ | ---------- | ---------------------------- |
| POST   | `/api/mst` | Generate optimized road plan |

### Projects

| Method | Endpoint              | Description             |
| ------ | --------------------- | ----------------------- |
| POST   | `/api/projects`       | Save a planning project |
| GET    | `/api/projects`       | List user's projects    |
| GET    | `/api/projects/{pid}` | Load a project          |
| DELETE | `/api/projects/{pid}` | Delete a project        |

### System

| Method | Endpoint      | Description  |
| ------ | ------------- | ------------ |
| GET    | `/api/health` | Health check |

---

## 📥 Example Planning Request

After authentication, send a scenario to `/api/mst` using a Bearer token.

```json
{
  "villages": [
    { "id": 1, "name": "Village A", "population": 2500 },
    { "id": 2, "name": "Village B", "population": 1800 },
    { "id": 3, "name": "Village C", "population": 3200 }
  ],
  "roads": [
    {
      "a": 1,
      "b": 2,
      "cost": 20,
      "quality": 8,
      "flood": 10,
      "maintenance": 2,
      "length": 8
    },
    {
      "a": 2,
      "b": 3,
      "cost": 25,
      "quality": 7,
      "flood": 20,
      "maintenance": 3,
      "length": 10
    },
    {
      "a": 1,
      "b": 3,
      "cost": 40,
      "quality": 9,
      "flood": 5,
      "maintenance": 2,
      "length": 14
    }
  ],
  "budget": 60,
  "cost_multiplier": 1,
  "weather": 20,
  "min_quality": 1
}
```

The response contains the selected roads, rejected roads, total cost, budget information, risk indicators, environmental estimates, and execution time.

---

## 🌱 Impact

### Economic Impact

- Helps minimize construction expenditure.
- Supports budget-aware infrastructure planning.
- Avoids unnecessary road construction.

### Social Impact

- Supports better village connectivity.
- Can assist rural infrastructure development.
- Helps planners evaluate connectivity decisions systematically.

### Environmental Considerations

The current prototype estimates road length, trees removed, CO₂ impact, saplings to plant, and a green score to provide an additional environmental perspective during planning.

### Governance Impact

- Provides explainable road-selection reasons.
- Creates a structured planning workflow.
- Supports transparent, data-driven infrastructure decisions.

---

## 🔮 Future Scope

The current system can be extended with:

- GIS and interactive map integration.
- Real-world geospatial road data.
- Satellite imagery integration.
- Machine-learning-based construction cost prediction.
- Traffic-aware infrastructure planning.
- Real-time weather and flood data.
- Advanced route and accessibility analysis.
- Cloud deployment and scalable infrastructure.
- Role-based government user management.
- Advanced dashboards and analytics.
- Mobile application support.

---

## 🔒 Security Notes

For production deployment:

- Use a strong randomly generated `SECRET_KEY`.
- Never commit secrets or credentials to GitHub.
- Replace demo users with database-backed authentication.
- Restrict `CORS_ORIGINS` to trusted frontend domains.
- Use HTTPS in production.
- Add rate limiting and audit logging where appropriate.
- Store sensitive configuration through environment variables or a secrets manager.

---

## 📌 Project Highlights

**Problem:** Connect all villages at minimum construction cost.

**Core Algorithm:** Kruskal's Minimum Spanning Tree.

**Optimization:** Effective road cost considering scenario factors such as weather and flood risk.

**Backend:** FastAPI + Python.

**Database:** MongoDB.

**Security:** JWT + bcrypt.

**Deployment:** Docker + Docker Compose.

**Documentation:** Swagger UI + ReDoc.

---

## 👥 Team

**Team No:** 1

| Member     | Roll Number  |
| ---------- | ------------ |
| Teekshitha | 25MVCSER0105 |
| Akshara    | 25MVCSER0156 |
| Sathwika   | 25MVCSER0138 |

---

## 📜 License

This project was developed as a hackathon/academic prototype. Add the appropriate open-source license if you intend to distribute the source code publicly.

---

### SmartRoad AI

**Connecting villages intelligently. Optimizing infrastructure efficiently.**
