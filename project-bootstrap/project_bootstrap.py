#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_PYTHON = "3.11"
CORE_DEPENDENCIES = [
    "fastapi", "uvicorn", "pandas", "numpy", "scikit-learn",
    "sqlalchemy", "psycopg2-binary", "python-dotenv", "requests",
]
PROJECT_DIRECTORIES = [
    "backend/app/api", "backend/app/core", "backend/app/models",
    "backend/app/schemas", "backend/app/services", "backend/tests",
    "pipelines/ingestion", "pipelines/processing", "pipelines/feature_engineering",
    "models/training", "models/evaluation", "models/inference", "models/artifacts",
    "notebooks", "database/migrations", "database/scripts",
    "data/raw", "data/processed", "data/external", "mlflow",
    "tests/unit", "tests/integration", "docs/architecture", "scripts",
    ".github/workflows",
]

GITIGNORE = """.env
.env.local
.env.production
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
.ruff_cache/
.ipynb_checkpoints/
frontend/node_modules/
frontend/dist/
data/raw/*
data/processed/*
data/external/*
!data/raw/.gitkeep
!data/processed/.gitkeep
!data/external/.gitkeep
models/artifacts/*
!models/artifacts/.gitkeep
mlruns/
mlartifacts/
mlflow.db
.DS_Store
*.log
"""

ENV_EXAMPLE = """APP_ENV=development
APP_HOST=127.0.0.1
APP_PORT=8000
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
DATABASE_URL=
WEATHER_API_KEY=
WEATHER_API_BASE_URL=
MLFLOW_TRACKING_URI=http://127.0.0.1:5000
VITE_API_BASE_URL=http://127.0.0.1:8000
"""

FASTAPI_MAIN = '''from fastapi import FastAPI

app = FastAPI(title="Project API", version="0.1.0")

@app.get("/")
def root() -> dict[str, str]:
    return {"message": "API is running."}

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}
'''

MLFLOW_EXAMPLE = '''import mlflow
import mlflow.sklearn
from sklearn.datasets import load_diabetes
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split


def main() -> None:
    dataset = load_diabetes()
    x_train, x_test, y_train, y_test = train_test_split(
        dataset.data, dataset.target, test_size=0.20, random_state=42
    )
    params = {"n_estimators": 100, "max_depth": 6, "random_state": 42}
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
'''


def header(message: str) -> None:
    print("\n" + "=" * 70)
    print(message)
    print("=" * 70)


def run_command(command: list[str], cwd: Path | None = None) -> None:
    print("\n$", " ".join(command))
    subprocess.run(command, cwd=cwd, check=True)


def ask_yes_no(question: str, default: bool = True) -> bool:
    prompt = "Y/n" if default else "y/N"
    while True:
        value = input(f"{question} [{prompt}]: ").strip().lower()
        if not value:
            return default
        if value in {"y", "yes"}:
            return True
        if value in {"n", "no"}:
            return False
        print("Please enter y or n.")


def sanitize_project_name(name: str) -> str:
    name = re.sub(r"[\s_]+", "-", name.strip().lower())
    name = re.sub(r"[^a-z0-9-]", "", name)
    return re.sub(r"-+", "-", name).strip("-")


def write_file(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"Created: {path}")


def check_tools(include_react: bool, include_git: bool) -> None:
    tools = ["python3", "poetry"]
    if include_react:
        tools += ["node", "npm"]
    if include_git:
        tools += ["git"]
    missing = [tool for tool in tools if shutil.which(tool) is None]
    if missing:
        raise RuntimeError("Missing tools: " + ", ".join(missing))


def create_structure(project_path: Path) -> None:
    for directory in PROJECT_DIRECTORIES:
        (project_path / directory).mkdir(parents=True, exist_ok=True)
    for directory in ["data/raw", "data/processed", "data/external", "models/artifacts"]:
        write_file(project_path / directory / ".gitkeep")


def configure_poetry(project_path: Path, project_name: str, python_version: str,
                     include_supabase: bool, include_mlflow: bool, include_jupyter: bool) -> None:
    pyproject = f'''[tool.poetry]\nname = "{project_name}"\nversion = "0.1.0"\ndescription = "Full-stack machine learning and AI application"\nauthors = []\npackage-mode = false\n\n[tool.poetry.dependencies]\npython = "^{python_version}"\n\n[tool.poetry.group.dev.dependencies]\n\n[build-system]\nrequires = ["poetry-core"]\nbuild-backend = "poetry.core.masonry.api"\n'''
    write_file(project_path / "pyproject.toml", pyproject)
    run_command(["poetry", "config", "virtualenvs.in-project", "true", "--local"], cwd=project_path)

    python_cmd = f"python{python_version}"
    if shutil.which(python_cmd):
        run_command(["poetry", "env", "use", python_cmd], cwd=project_path)

    run_command(["poetry", "add", *CORE_DEPENDENCIES], cwd=project_path)
    if include_supabase:
        run_command(["poetry", "add", "supabase"], cwd=project_path)
    if include_mlflow:
        run_command(["poetry", "add", "mlflow"], cwd=project_path)

    dev = ["pytest", "ruff"]
    if include_jupyter:
        dev += ["jupyterlab", "ipykernel"]
    run_command(["poetry", "add", "--group", "dev", *dev], cwd=project_path)


def configure_jupyter(project_path: Path, project_name: str) -> None:
    display = f"Python ({project_name.replace('-', ' ').title()})"
    run_command([
        "poetry", "run", "python", "-m", "ipykernel", "install", "--user",
        "--name", project_name, "--display-name", display
    ], cwd=project_path)


def create_react(project_path: Path) -> None:
    run_command(["npm", "create", "vite@latest", "frontend", "--", "--template", "react"], cwd=project_path)
    run_command(["npm", "install"], cwd=project_path / "frontend")
    write_file(project_path / "frontend" / ".env.example", "VITE_API_BASE_URL=http://127.0.0.1:8000\n")


def create_scripts(project_path: Path, include_jupyter: bool, include_mlflow: bool, include_react: bool) -> None:
    scripts = {
        "start_backend.sh": '#!/bin/bash\nset -e\npoetry run uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000\n'
    }
    if include_jupyter:
        scripts["start_jupyter.sh"] = '#!/bin/bash\nset -e\npoetry run jupyter lab\n'
    if include_mlflow:
        scripts["start_mlflow.sh"] = '#!/bin/bash\nset -e\npoetry run mlflow server --host 127.0.0.1 --port 5000\n'
    if include_react:
        scripts["start_frontend.sh"] = '#!/bin/bash\nset -e\ncd frontend\nnpm run dev\n'

    for name, content in scripts.items():
        path = project_path / "scripts" / name
        write_file(path, content)
        path.chmod(path.stat().st_mode | 0o111)


def main() -> None:
    header("Full-Stack / ML Project Bootstrapper")
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
        return

    python_version = input(f"Python version [{DEFAULT_PYTHON}]: ").strip() or DEFAULT_PYTHON
    include_react = ask_yes_no("Create React/Vite frontend?")
    include_supabase = ask_yes_no("Install Supabase Python client?")
    include_jupyter = ask_yes_no("Install JupyterLab and register kernel?")
    include_mlflow = ask_yes_no("Install MLflow?")
    include_git = ask_yes_no("Initialize Git repository?")

    check_tools(include_react, include_git)
    project_path.mkdir(parents=True)
    create_structure(project_path)
    write_file(project_path / ".gitignore", GITIGNORE)
    write_file(project_path / ".env.example", ENV_EXAMPLE)
    write_file(project_path / "backend" / "__init__.py")
    write_file(project_path / "backend" / "app" / "__init__.py")
    for pkg in ["api", "core", "models", "schemas", "services"]:
        write_file(project_path / "backend" / "app" / pkg / "__init__.py")
    write_file(project_path / "backend" / "app" / "main.py", FASTAPI_MAIN)
    if include_mlflow:
        write_file(project_path / "models" / "training" / "mlflow_example.py", MLFLOW_EXAMPLE)

    configure_poetry(project_path, project_name, python_version,
                     include_supabase, include_mlflow, include_jupyter)
    if include_jupyter:
        configure_jupyter(project_path, project_name)
    if include_react:
        create_react(project_path)
    create_scripts(project_path, include_jupyter, include_mlflow, include_react)
    if include_git:
        run_command(["git", "init"], cwd=project_path)
        run_command(["git", "branch", "-M", "main"], cwd=project_path)

    header("Project created successfully")
    print(project_path)
    print("\nNext steps:")
    print(f'  cd "{project_path}"')
    print("  cp .env.example .env")
    print("  poetry env info")
    if include_jupyter:
        print("  ./scripts/start_jupyter.sh")
    if include_mlflow:
        print("  ./scripts/start_mlflow.sh")
    print("  ./scripts/start_backend.sh")
    if include_react:
        print("  ./scripts/start_frontend.sh")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(130)
    except (subprocess.CalledProcessError, RuntimeError) as exc:
        print(f"\nBootstrap failed: {exc}")
        sys.exit(1)
