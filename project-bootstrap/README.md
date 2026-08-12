# Project Bootstrapper v3.2

Version 3.2 separates project provisioning from development runtime management.

## Completion behavior

The bootstrapper does **not** automatically start npm/Vite, FastAPI, JupyterLab,
MLflow, Go ingestion, or other long-running development services.

The workflow is:

```text
Bootstrap
   ↓
Validate
   ↓
Print component report
   ↓
Print next-step commands
   ↓
Acknowledge completion
   ↓
Optionally open a new Terminal window
   ↓
Exit
```

After the component report, the bootstrapper prints commands for the selected
features, such as:

```bash
./scripts/start_backend.sh
./scripts/start_frontend.sh
./scripts/start_jupyter.sh
./scripts/start_mlflow.sh
./scripts/start_go_ingestion.sh
```

It then confirms:

```text
Bootstrap Complete
Project bootstrap completed.
No development servers were started automatically.
```

## Optional macOS Terminal window

After completion, the utility asks:

```text
Open the project directory in a new Terminal window? [y/N]:
```

The default is `No`.

If selected on macOS, a new Terminal window opens and changes into the newly
created project directory. It does not start npm, Vite, FastAPI, JupyterLab,
MLflow, or Go ingestion.

## Why this design

Bootstrap logic should provision and validate a project, then terminate cleanly.
Long-running development processes remain explicit developer actions. This keeps
the utility easier to debug, safer to rerun, and better suited to future Docker
and cloud deployment workflows.

## Typical workflow

Run:

```bash
python3 project_bootstrap_v3_2.py
```

After completion, start only the services needed for the current session.

Frontend:

```bash
./scripts/start_frontend.sh
```

Backend:

```bash
./scripts/start_backend.sh
```

JupyterLab:

```bash
./scripts/start_jupyter.sh
```

MLflow:

```bash
./scripts/start_mlflow.sh
```

Go ingestion:

```bash
./scripts/start_go_ingestion.sh
```

## Ingestion options retained from v3.1

```text
1. Python
2. Go
3. Both Python and Go
```

## Recommended multi-terminal development pattern

```text
Terminal 1  FastAPI
Terminal 2  React / Vite
Terminal 3  MLflow
Terminal 4  JupyterLab
Terminal 5  Go ingestion
```

Only start the processes needed for the current development session.

## Retained capabilities

- Python 3.12 minor-version constraint
- Poetry in-project `.venv`
- pandas `>=2.2,<3`
- MLflow
- JupyterLab with a named project kernel
- React + Vite
- Supabase / PostgreSQL support
- Python, Go, or dual ingestion
- Git initialization
- final component status reporting
