#!/usr/bin/env python3
"""Project Bootstrapper v3.1

Reusable full-stack / ML / AI project scaffolding with optional Python or Go
API-to-database ingestion services.
"""
from __future__ import annotations

import re
import platform
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

VERSION = "3.2.0"
DEFAULT_PYTHON = "3.12"

BASE_DEPENDENCIES = [
    "fastapi",
    "uvicorn",
    "sqlalchemy",
    "psycopg2-binary",
    "python-dotenv",
    "requests",
]

DATA_SCIENCE_STACK = [
    "pandas>=2.2,<3",
    "numpy",
    "scikit-learn",
]

ML_STACK = [
    "pandas>=2.2,<3",
    "numpy",
    "scikit-learn",
    "mlflow",
]

DEV_DEPENDENCIES = ["pytest", "ruff"]
JUPYTER_DEPENDENCIES = ["jupyterlab", "ipykernel"]

PROJECT_DIRECTORIES = [
    "backend/app/api",
    "backend/app/core",
    "backend/app/models",
    "backend/app/schemas",
    "backend/app/services",
    "backend/tests",
    "pipelines/ingestion",
    "pipelines/processing",
    "pipelines/feature_engineering",
    "models/training",
    "models/evaluation",
    "models/inference",
    "models/artifacts",
    "notebooks/exploration",
    "notebooks/modeling",
    "database/migrations",
    "database/scripts",
    "data/raw",
    "data/processed",
    "data/external",
    "tests/unit",
    "tests/integration",
    "docs/architecture",
    "scripts",
    ".github/workflows",
]

GO_DIRECTORIES = [
    "ingestion-go/cmd/weather-ingest",
    "ingestion-go/internal/api",
    "ingestion-go/internal/config",
    "ingestion-go/internal/database",
]

GITIGNORE = r'''# Environment and secrets
.env
.env.*
!.env.example

# Python
__pycache__/
*.py[cod]
*.egg-info/
.pytest_cache/
.mypy_cache/
.ruff_cache/
.venv/

# Jupyter
.ipynb_checkpoints/

# React / Node
frontend/node_modules/
frontend/dist/
frontend/build/

# Go
*.test
*.out

# Local data
data/raw/*
data/processed/*
data/external/*
!data/raw/.gitkeep
!data/processed/.gitkeep
!data/external/.gitkeep

# ML artifacts
models/artifacts/*
!models/artifacts/.gitkeep

# MLflow
mlruns/
mlartifacts/
mlflow.db

# IDE / OS
.vscode/
.idea/
.DS_Store

# Logs
*.log
logs/
'''.strip()

ENV_EXAMPLE = r'''# Application
APP_ENV=development
APP_HOST=127.0.0.1
APP_PORT=8000

# Supabase
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=

# PostgreSQL
DATABASE_URL=

# WeatherFlow / OpenWeather
WEATHERFLOW_OPENWEATHER_API_KEY=
OPENWEATHER_BASE_URL=https://api.openweathermap.org

# MLflow
MLFLOW_TRACKING_URI=http://127.0.0.1:5000

# React / Vite
VITE_API_BASE_URL=http://127.0.0.1:8000
'''.strip()

FASTAPI_MAIN = r'''from fastapi import FastAPI

app = FastAPI(
    title="Project API",
    description="Full-stack machine learning application API",
    version="0.1.0",
)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "API is running."}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}
'''.strip()

MLFLOW_EXAMPLE = r'''import mlflow
import mlflow.sklearn
from sklearn.datasets import load_diabetes
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split


def main() -> None:
    dataset = load_diabetes()
    x_train, x_test, y_train, y_test = train_test_split(
        dataset.data,
        dataset.target,
        test_size=0.20,
        random_state=42,
    )

    params = {
        "n_estimators": 100,
        "max_depth": 6,
        "random_state": 42,
    }

    mlflow.set_experiment("baseline-model")

    with mlflow.start_run():
        model = RandomForestRegressor(**params)
        model.fit(x_train, y_train)
        predictions = model.predict(x_test)
        mse = mean_squared_error(y_test, predictions)
        mlflow.log_params(params)
        mlflow.log_metric("mse", mse)
        mlflow.sklearn.log_model(model, name="model")
        print(f"MSE: {mse:.4f}")


if __name__ == "__main__":
    main()
'''.strip()

GO_MAIN = r'''package main

import (
    "context"
    "fmt"
    "log"
    "time"

    "{module_name}/internal/api"
    "{module_name}/internal/config"
)

func main() {{
    cfg := config.Load()

    client := api.NewOpenWeatherClient(
        cfg.OpenWeatherBaseURL,
        cfg.OpenWeatherAPIKey,
    )

    ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()

    payload, err := client.FetchCurrentWeather(ctx, "Chicago")
    if err != nil {{
        log.Fatal(err)
    }}

    fmt.Printf("Weather payload received: %d bytes\n", len(payload))
}}
'''.strip()

GO_CONFIG = r'''package config

import "os"

type Config struct {
    OpenWeatherAPIKey  string
    OpenWeatherBaseURL string
    DatabaseURL        string
}

func Load() Config {
    return Config{
        OpenWeatherAPIKey: os.Getenv("WEATHERFLOW_OPENWEATHER_API_KEY"),
        OpenWeatherBaseURL: getenv(
            "OPENWEATHER_BASE_URL",
            "https://api.openweathermap.org",
        ),
        DatabaseURL: os.Getenv("DATABASE_URL"),
    }
}

func getenv(key, fallback string) string {
    if value := os.Getenv(key); value != "" {
        return value
    }
    return fallback
}
'''.strip()

GO_API_CLIENT = r'''package api

import (
    "context"
    "fmt"
    "io"
    "net/http"
    "net/url"
)

type OpenWeatherClient struct {
    baseURL string
    apiKey  string
    client  *http.Client
}

func NewOpenWeatherClient(baseURL, apiKey string) *OpenWeatherClient {
    return &OpenWeatherClient{
        baseURL: baseURL,
        apiKey:  apiKey,
        client:  &http.Client{},
    }
}

func (c *OpenWeatherClient) FetchCurrentWeather(
    ctx context.Context,
    city string,
) ([]byte, error) {
    endpoint, err := url.Parse(c.baseURL + "/data/2.5/weather")
    if err != nil {
        return nil, err
    }

    query := endpoint.Query()
    query.Set("q", city)
    query.Set("appid", c.apiKey)
    endpoint.RawQuery = query.Encode()

    req, err := http.NewRequestWithContext(
        ctx,
        http.MethodGet,
        endpoint.String(),
        nil,
    )
    if err != nil {
        return nil, err
    }

    resp, err := c.client.Do(req)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    if resp.StatusCode < 200 || resp.StatusCode >= 300 {
        return nil, fmt.Errorf("OpenWeather request failed: %s", resp.Status)
    }

    return io.ReadAll(resp.Body)
}
'''.strip()

GO_DATABASE = r'''package database

// Package database is reserved for PostgreSQL / Supabase persistence.
//
// A practical next step is to add pgx:
//
//     go get github.com/jackc/pgx/v5
//
// Then implement connection pooling and INSERT/UPSERT operations here.
'''.strip()

GO_START_SCRIPT = r'''#!/bin/bash
set -e
cd ingestion-go
go run ./cmd/weather-ingest
'''

START_BACKEND = r'''#!/bin/bash
set -e
poetry run uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
'''
START_JUPYTER = r'''#!/bin/bash
set -e
poetry run jupyter lab
'''
START_MLFLOW = r'''#!/bin/bash
set -e
poetry run mlflow server --host 127.0.0.1 --port 5000
'''
START_FRONTEND = r'''#!/bin/bash
set -e
cd frontend
npm run dev
'''


@dataclass
class BootstrapReport:
    statuses: dict[str, str] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def success(self, component: str) -> None:
        self.statuses[component] = "OK"

    def skipped(self, component: str) -> None:
        self.statuses[component] = "SKIPPED"

    def failed(self, component: str, message: str) -> None:
        self.statuses[component] = "FAILED"
        self.warnings.append(f"{component}: {message}")

    def print_report(self) -> None:
        header("Bootstrap Report")
        for component, status in self.statuses.items():
            marker = {"OK": "✓", "SKIPPED": "-", "FAILED": "✗"}.get(status, "?")
            print(f"{marker} {component}: {status}")

        if self.warnings:
            print("\nItems requiring attention:")
            for warning in self.warnings:
                print(f"  - {warning}")
        else:
            print("\nAll selected components completed successfully.")


def header(message: str) -> None:
    print("\n" + "=" * 72)
    print(message)
    print("=" * 72)


def command_exists(command: str) -> bool:
    return shutil.which(command) is not None


def run_command(command: list[str], cwd: Path | None = None, required: bool = True) -> bool:
    print("\n$", " ".join(command))
    try:
        subprocess.run(command, cwd=cwd, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as error:
        print(f"\nCommand failed: {error}")
        if required:
            raise
        return False


def ask_yes_no(question: str, default: bool = True) -> bool:
    prompt = "Y/n" if default else "y/N"
    while True:
        answer = input(f"{question} [{prompt}]: ").strip().lower()
        if not answer:
            return default
        if answer in {"y", "yes"}:
            return True
        if answer in {"n", "no"}:
            return False
        print("Please enter y or n.")


def choose_ingestion_language() -> str:
    print("\nData ingestion implementation:")
    print("  1. Python")
    print("  2. Go")
    print("  3. Both Python and Go")
    while True:
        choice = input("Selection [1]: ").strip() or "1"
        if choice == "1":
            return "python"
        if choice == "2":
            return "go"
        if choice == "3":
            return "both"
        print("Please select 1, 2, or 3.")


def sanitize_project_name(name: str) -> str:
    name = re.sub(r"[\s_]+", "-", name.strip().lower())
    name = re.sub(r"[^a-z0-9-]", "", name)
    return re.sub(r"-+", "-", name).strip("-")


def display_project_name(name: str) -> str:
    return name.replace("-", " ").title()


def python_constraint(version: str) -> str:
    parts = version.split(".")
    if len(parts) != 2 or not all(part.isdigit() for part in parts):
        raise ValueError("Python version must look like 3.12.")
    major, minor = map(int, parts)
    return f">={major}.{minor},<{major}.{minor + 1}"


def write_file(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content + ("\n" if content and not content.endswith("\n") else ""), encoding="utf-8")
    print(f"Created: {path}")


def create_structure(project_path: Path, include_go: bool) -> None:
    directories = list(PROJECT_DIRECTORIES)
    if include_go:
        directories.extend(GO_DIRECTORIES)
    for directory in directories:
        (project_path / directory).mkdir(parents=True, exist_ok=True)
    for directory in ["data/raw", "data/processed", "data/external", "models/artifacts"]:
        write_file(project_path / directory / ".gitkeep")


def create_base_files(project_path: Path, project_name: str, python_version: str) -> None:
    pyproject = f'''[tool.poetry]\nname = "{project_name}"\nversion = "0.1.0"\ndescription = "Full-stack machine learning and AI application"\nauthors = []\npackage-mode = false\n\n[tool.poetry.dependencies]\npython = "{python_constraint(python_version)}"\n\n[tool.poetry.group.dev.dependencies]\n\n[build-system]\nrequires = ["poetry-core"]\nbuild-backend = "poetry.core.masonry.api"\n'''

    write_file(project_path / ".gitignore", GITIGNORE)
    write_file(project_path / ".env.example", ENV_EXAMPLE)
    write_file(project_path / "pyproject.toml", pyproject)
    write_file(project_path / "backend" / "__init__.py")
    write_file(project_path / "backend" / "app" / "__init__.py")

    for package in ["api", "core", "models", "schemas", "services"]:
        write_file(project_path / "backend" / "app" / package / "__init__.py")
    for package in ["ingestion", "processing", "feature_engineering"]:
        write_file(project_path / "pipelines" / package / "__init__.py")

    write_file(project_path / "backend" / "app" / "main.py", FASTAPI_MAIN)


def configure_poetry(project_path: Path, python_version: str, include_mlflow: bool, report: BootstrapReport) -> bool:
    header("Poetry")
    try:
        run_command(["poetry", "config", "virtualenvs.in-project", "true", "--local"], cwd=project_path)

        python_cmd = f"python{python_version}"
        if not command_exists(python_cmd):
            report.failed(
                "Poetry environment",
                f"{python_cmd} is not installed or not on PATH. Install Python {python_version}.x and rerun.",
            )
            return False

        run_command(["poetry", "env", "use", python_cmd], cwd=project_path)
        run_command(["poetry", "add", *BASE_DEPENDENCIES], cwd=project_path)
        stack = ML_STACK if include_mlflow else DATA_SCIENCE_STACK
        run_command(["poetry", "add", *stack], cwd=project_path)
        run_command(["poetry", "add", "--group", "dev", *DEV_DEPENDENCIES], cwd=project_path)

        report.success("Poetry environment")
        report.success("Core Python stack")
        if include_mlflow:
            report.success("MLflow")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as error:
        report.failed("Poetry environment", str(error))
        if include_mlflow:
            report.failed("MLflow", "ML dependency installation did not complete.")
        return False


def configure_supabase(project_path: Path, poetry_ready: bool, report: BootstrapReport) -> None:
    header("Supabase")
    if not poetry_ready:
        report.failed("Supabase", "Skipped because the Poetry environment was not ready.")
        return
    if run_command(["poetry", "add", "supabase"], cwd=project_path, required=False):
        report.success("Supabase")
    else:
        report.failed("Supabase", "Poetry could not install the Supabase client.")


def configure_jupyter(project_path: Path, project_name: str, poetry_ready: bool, report: BootstrapReport) -> None:
    header("JupyterLab")
    if not poetry_ready:
        report.failed("JupyterLab", "Skipped because the Poetry environment was not ready.")
        return
    if not run_command(
        ["poetry", "add", "--group", "dev", *JUPYTER_DEPENDENCIES],
        cwd=project_path,
        required=False,
    ):
        report.failed("JupyterLab", "Jupyter dependencies could not be installed.")
        return

    display_name = f"Python ({display_project_name(project_name)})"
    if run_command(
        [
            "poetry", "run", "python", "-m", "ipykernel", "install", "--user",
            "--name", project_name, "--display-name", display_name,
        ],
        cwd=project_path,
        required=False,
    ):
        report.success("JupyterLab")
        print(f"\nKernel: {display_name}")
    else:
        report.failed("JupyterLab", "Kernel registration failed.")


def configure_react(project_path: Path, report: BootstrapReport) -> None:
    header("React / Vite")
    if not command_exists("node") or not command_exists("npm"):
        report.failed("React / Vite", "Node.js and npm must be installed and on PATH.")
        return

    frontend = project_path / "frontend"
    if frontend.exists() and any(frontend.iterdir()):
        report.failed("React / Vite", "frontend/ already exists and is not empty.")
        return

    if not run_command(
        ["npm", "create", "vite@latest", "frontend", "--", "--template", "react"],
        cwd=project_path,
        required=False,
    ):
        report.failed("React / Vite", "Vite scaffolding failed.")
        return

    if run_command(["npm", "install"], cwd=frontend, required=False):
        write_file(frontend / ".env.example", "VITE_API_BASE_URL=http://127.0.0.1:8000")
        report.success("React / Vite")
    else:
        report.failed("React / Vite", "npm install failed.")


def configure_go_ingestion(project_path: Path, project_name: str, report: BootstrapReport) -> None:
    header("Go ingestion service")
    if not command_exists("go"):
        report.failed("Go ingestion", "Go is not installed or not available on PATH.")
        return

    go_root = project_path / "ingestion-go"
    module_name = f"example.com/{project_name}/ingestion-go"

    try:
        write_file(go_root / "go.mod", f"module {module_name}\n\ngo 1.23\n")
        write_file(
            go_root / "cmd" / "weather-ingest" / "main.go",
            GO_MAIN.format(module_name=module_name),
        )
        write_file(go_root / "internal" / "config" / "config.go", GO_CONFIG)
        write_file(go_root / "internal" / "api" / "openweather.go", GO_API_CLIENT)
        write_file(go_root / "internal" / "database" / "database.go", GO_DATABASE)
        run_command(["go", "fmt", "./..."], cwd=go_root, required=False)
        report.success("Go ingestion")
    except OSError as error:
        report.failed("Go ingestion", str(error))


def create_scripts(project_path: Path, include_jupyter: bool, include_mlflow: bool, include_react: bool, include_go: bool) -> None:
    scripts = {"start_backend.sh": START_BACKEND}
    if include_jupyter:
        scripts["start_jupyter.sh"] = START_JUPYTER
    if include_mlflow:
        scripts["start_mlflow.sh"] = START_MLFLOW
    if include_react:
        scripts["start_frontend.sh"] = START_FRONTEND
    if include_go:
        scripts["start_go_ingestion.sh"] = GO_START_SCRIPT

    for name, content in scripts.items():
        path = project_path / "scripts" / name
        write_file(path, content)
        path.chmod(path.stat().st_mode | 0o111)


def initialize_git(project_path: Path, report: BootstrapReport) -> None:
    header("Git")
    if not command_exists("git"):
        report.failed("Git", "git is not installed or not available on PATH.")
        return
    if run_command(["git", "init"], cwd=project_path, required=False) and run_command(
        ["git", "branch", "-M", "main"], cwd=project_path, required=False
    ):
        report.success("Git")
    else:
        report.failed("Git", "Repository initialization failed.")



def open_project_in_new_terminal(project_path: Path) -> bool:
    """Open macOS Terminal in the project directory without starting services."""
    if platform.system() != "Darwin":
        print(
            "Automatic Terminal opening is only supported by this helper on macOS."
        )
        return False

    safe_path = str(project_path).replace("\\", "\\\\").replace('"', '\\"')

    applescript = (
        'tell application "Terminal"\n'
        'activate\n'
        f'do script "cd \\"{safe_path}\\""\n'
        'end tell'
    )

    return run_command(
        ["osascript", "-e", applescript],
        required=False,
    )



def print_next_steps(project_path: Path, include_jupyter: bool, include_mlflow: bool, include_react: bool, include_go: bool) -> None:
    header("Next Steps")
    print(f'cd "{project_path}"')
    print("cp .env.example .env")
    print("poetry env info")
    print("poetry run python --version")
    print("./scripts/start_backend.sh")
    if include_jupyter:
        print("./scripts/start_jupyter.sh")
    if include_mlflow:
        print("./scripts/start_mlflow.sh")
    if include_react:
        print("./scripts/start_frontend.sh")
    if include_go:
        print("./scripts/start_go_ingestion.sh")


def main() -> None:
    report = BootstrapReport()
    header(f"Project Bootstrapper v{VERSION}")

    default_root = Path.home() / "Projects"
    root_input = input(f"Root directory [{default_root}]: ").strip()
    root = Path(root_input).expanduser() if root_input else default_root
    root.mkdir(parents=True, exist_ok=True)

    raw_name = input("Project name: ").strip()
    if not raw_name:
        print("Project name is required.")
        return

    project_name = sanitize_project_name(raw_name)
    project_path = root / project_name
    if project_path.exists():
        print(f"Project already exists: {project_path}")
        print("This bootstrapper will not overwrite an existing project.")
        return

    python_version = input(f"Python version [{DEFAULT_PYTHON}]: ").strip() or DEFAULT_PYTHON
    try:
        constraint = python_constraint(python_version)
    except ValueError as error:
        print(error)
        return

    ingestion_language = choose_ingestion_language()
    include_go = ingestion_language in {"go", "both"}
    include_react = ask_yes_no("Create React/Vite frontend?")
    include_supabase = ask_yes_no("Install Supabase Python client?")
    include_jupyter = ask_yes_no("Install JupyterLab and register kernel?")
    include_mlflow = ask_yes_no("Install MLflow?")
    include_git = ask_yes_no("Initialize Git repository?")

    header("Configuration")
    print(f"Project:       {display_project_name(project_name)}")
    print(f"Path:          {project_path}")
    print(f"Python:        {python_version}.x")
    print(f"Constraint:    {constraint}")
    print(f"Ingestion:     {ingestion_language}")
    print(f"React/Vite:    {include_react}")
    print(f"Supabase:      {include_supabase}")
    print(f"JupyterLab:    {include_jupyter}")
    print(f"MLflow:        {include_mlflow}")
    print(f"Git:           {include_git}")

    if not ask_yes_no("\nCreate project?"):
        print("Cancelled.")
        return

    if not command_exists("poetry"):
        print("\nPoetry is required but was not found on PATH.")
        return

    project_path.mkdir(parents=True)

    try:
        create_structure(project_path, include_go)
        create_base_files(project_path, project_name, python_version)
        if include_mlflow:
            write_file(project_path / "models" / "training" / "mlflow_example.py", MLFLOW_EXAMPLE)
        create_scripts(project_path, include_jupyter, include_mlflow, include_react, include_go)
        report.success("Project structure")
    except OSError as error:
        report.failed("Project structure", str(error))
        report.print_report()
        return

    poetry_ready = configure_poetry(project_path, python_version, include_mlflow, report)

    if include_supabase:
        configure_supabase(project_path, poetry_ready, report)
    else:
        report.skipped("Supabase")

    if include_jupyter:
        configure_jupyter(project_path, project_name, poetry_ready, report)
    else:
        report.skipped("JupyterLab")

    if include_go:
        configure_go_ingestion(project_path, project_name, report)
    else:
        report.skipped("Go ingestion")

    if include_react:
        configure_react(project_path, report)
    else:
        report.skipped("React / Vite")

    if include_git:
        initialize_git(project_path, report)
    else:
        report.skipped("Git")

    if not include_mlflow:
        report.skipped("MLflow")

    report.print_report()
    print_next_steps(project_path, include_jupyter, include_mlflow, include_react, include_go)

    header("Bootstrap Complete")
    print(f"Project bootstrap completed for: {project_path}")
    print("No development servers were started automatically.")

    if ask_yes_no(
        "Open the project directory in a new Terminal window?",
        default=False,
    ):
        if open_project_in_new_terminal(project_path):
            print("Opened a new Terminal window in the project directory.")
        else:
            print("Could not open a new Terminal window automatically.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        sys.exit(130)
