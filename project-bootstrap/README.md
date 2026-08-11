# Full-Stack / ML Project Bootstrapper

A reusable command-line utility for creating full-stack, data science, ML engineering, and AI engineering projects.

## Default stack

Python 3.11, Poetry, FastAPI, React/Vite, Supabase/PostgreSQL, JupyterLab, ipykernel, MLflow, pandas, NumPy, scikit-learn, SQLAlchemy, pytest, Ruff, and Git.

## Run

```bash
python3 project_bootstrap.py
```

Or:

```bash
chmod +x project_bootstrap.py
./project_bootstrap.py
```

The utility asks for the root directory first, then the project name and optional features.

## Recommended selections for WeatherFlow-style projects

Choose Yes for React/Vite, Supabase, JupyterLab, MLflow, and Git.

## Jupyter

The Poetry environment is registered as a named Jupyter kernel. Start it with:

```bash
./scripts/start_jupyter.sh
```

## MLflow

Start the MLflow tracking server with:

```bash
./scripts/start_mlflow.sh
```

Then open `http://127.0.0.1:5000`.

## FastAPI

```bash
./scripts/start_backend.sh
```

API docs are available at `http://127.0.0.1:8000/docs`.

## React/Vite

```bash
./scripts/start_frontend.sh
```

## Environment variables

```bash
cp .env.example .env
```

Never commit `.env`.

## Intel macOS notes

The bootstrapper does not use Apple Silicon-specific tooling. It attempts to use the requested interpreter, such as `python3.11`, when available.
