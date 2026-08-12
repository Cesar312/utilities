# Project Bootstrapper 

A reusable command-line bootstrap utility for creating portfolio-grade full-stack,
data science, machine learning, ML engineering, and AI engineering projects.

Version 3.1 adds an optional Go-based data-ingestion service so projects can use
Python, Go, or both for ingestion workflows.

## Supported Stack

- Python 3.12
- Poetry
- FastAPI
- React
- Vite
- Supabase / PostgreSQL
- JupyterLab
- ipykernel
- MLflow
- pandas
- NumPy
- scikit-learn
- SQLAlchemy
- pytest
- Ruff
- Go
- Docker
- Git

## Ingestion Options

During setup, the bootstrapper asks which ingestion implementation to create:

```text
1. Python
2. Go
3. Both Python and Go
```

### Python ingestion

Use Python for API access, transformation, feature engineering, and persistence.

### Go ingestion

Use Go as a lightweight ingestion service for retrieving API data and writing
to PostgreSQL or Supabase.

### Both

Use Go for operational ingestion and Python for analytics, notebooks, modeling,
and ML workflows.

## Example Architecture

```text
OpenWeather API
      |
      v
+-----------------+
| Go Ingestion    |
| Service         |
+--------+--------+
         |
         v
+-----------------+
| Supabase /      |
| PostgreSQL      |
+--------+--------+
         |
         v
+-----------------------------+
| Python ML Environment       |
|                             |
| Jupyter -> Feature Eng.     |
|         -> Model Training   |
|         -> MLflow           |
+-------------+---------------+
              |
              v
        +-----------+
        | FastAPI   |
        +-----+-----+
              |
              v
        +-----------+
        | React UI  |
        +-----------+
```

## Prerequisites

Verify the tools you plan to use:

```bash
python3 --version
python3.12 --version
poetry --version
node --version
npm --version
git --version
go version
docker --version
```

Only the tools corresponding to selected features are required. Go is only
required if you select Go ingestion.

## Run the Bootstrapper

```bash
python3 project_bootstrap_v3_1.py
```

Or make it executable:

```bash
chmod +x project_bootstrap_v3_1.py
./project_bootstrap_v3_1.py
```

## Setup Workflow

The utility prompts for:

1. Root directory
2. Project name
3. Python version
4. Ingestion implementation
   - Python
   - Go
   - Both
5. React/Vite
6. Supabase Python client
7. JupyterLab and named kernel
8. MLflow
9. Docker
10. Git
11. Final confirmation

## Python Environment

The bootstrapper uses Poetry and configures an in-project virtual environment:

```text
project/.venv
```

For Python 3.12, the generated project constraint is:

```toml
python = ">=3.12,<3.13"
```

Verify:

```bash
poetry env info
poetry run python --version
```

## ML Compatibility

The bootstrapper constrains pandas to:

```text
pandas>=2.2,<3
```

This avoids dependency conflicts with MLflow versions that require pandas below 3.

## JupyterLab

List kernels:

```bash
jupyter kernelspec list
```

Start JupyterLab:

```bash
./scripts/start_jupyter.sh
```

## MLflow

Start MLflow:

```bash
./scripts/start_mlflow.sh
```

Open:

```text
http://127.0.0.1:5000
```

A starter experiment is generated at:

```text
models/training/mlflow_example.py
```

Run it with:

```bash
poetry run python models/training/mlflow_example.py
```

## FastAPI

Start the backend:

```bash
./scripts/start_backend.sh
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

## React / Vite

Start the frontend:

```bash
./scripts/start_frontend.sh
```

Vite normally runs at:

```text
http://localhost:5173
```

## Go Ingestion Service

If Go is selected, the bootstrapper creates:

```text
ingestion-go/
├── go.mod
├── cmd/
│   └── weather-ingest/
│       └── main.go
└── internal/
    ├── api/
    │   └── openweather.go
    ├── config/
    │   └── config.go
    └── database/
        └── database.go
```

Run it with:

```bash
./scripts/start_go_ingestion.sh
```

The generated starter implementation retrieves current weather data from OpenWeather.

The database package is intentionally left as an extension point for
PostgreSQL or Supabase persistence.

A logical next step is:

```bash
cd ingestion-go
go get github.com/jackc/pgx/v5
```

Then implement inserts in:

```text
ingestion-go/internal/database/database.go
```

## Environment Variables

Create a local environment file:

```bash
cp .env.example .env
```

Relevant variables include:

```env
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
DATABASE_URL=

WEATHERFLOW_OPENWEATHER_API_KEY=
OPENWEATHER_BASE_URL=

MLFLOW_TRACKING_URI=http://127.0.0.1:5000
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Never commit `.env`.

## Generated Project Structure

```text
project/
├── .venv/
├── backend/
├── frontend/
├── ingestion-go/
├── pipelines/
├── notebooks/
├── models/
├── database/
├── data/
├── tests/
├── docs/
├── scripts/
├── .github/workflows/
├── .env.example
├── .gitignore
├── docker-compose.yml
├── poetry.lock
├── pyproject.toml
└── README.md
```

## Recommended WeatherFlow Configuration

```text
Ingestion:        Both Python and Go
Frontend:         React + Vite
Backend API:      FastAPI
Database:         Supabase / PostgreSQL
Data Science:     JupyterLab
Model Tracking:   MLflow
Deployment:       Docker-ready
Source Control:   Git
```

A clean division of responsibilities is:

```text
Go
- External API ingestion
- Scheduling-friendly data collection
- Database persistence

Python
- EDA
- Feature engineering
- Model training
- Evaluation
- MLflow
- Inference APIs

React
- Current conditions
- Historical trends
- Forecast visualization
```

## macOS Notes

The bootstrapper is designed to work on macOS, including Intel-based Macs.

Verify Python:

```bash
which python3.12
python3.12 --version
poetry --version
```

Verify Go:

```bash
which go
go version
```

## Version 3.1 Improvements

- Explicit Python minor-version constraints
- pandas compatibility constraint for MLflow
- Improved ML dependency resolution
- Python, Go, or dual ingestion options
- Go OpenWeather client scaffold
- Go configuration package
- Go database extension point
- Go helper run script
- Jupyter kernel registration
- MLflow starter experiment
- React/Vite scaffolding
- Supabase support
- Docker configuration
- Git initialization
- Final bootstrap status reporting

## Suggested Future Enhancements

Potential next-version additions:

- Typer + Rich CLI
- Config-file driven profiles
- GitHub repository creation
- GitHub Actions templates
- pre-commit hooks
- Supabase migration templates
- pgx-backed Go persistence
- cron or scheduler support
- MLflow PostgreSQL backend
- Render / Vercel / AWS / Azure / GCP deployment profiles
- Generative AI / RAG project template
