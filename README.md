# MAUSAM — Backend

FastAPI backend for MAUSAM, a personalized weather-app homepage with disaster-management focus. Serves weather data, forecasts, alerts, and persona-based recommendations to the React Native frontend.

## Tech Stack
- **Framework:** FastAPI (Python)
- **Server:** Uvicorn
- **Database:** PostgreSQL (planned)
- **Weather Data:** Mock data now → OpenWeatherMap → IMD (real government API) later. Response shape stays identical across all three, so the frontend never needs to change.

## Prerequisites
- Python 3.12 (⚠️ not 3.14 — some packages like `pydantic-core` don't yet have pre-built Windows wheels for 3.14 and will fail to install)

To check your Python version:
```bash
python --version
```

If you're on Windows and don't have Python 3.12, install it via the Python launcher:
```bash
py install 3.12
```

## Setup

### 1. Create a virtual environment

```bash
py -3.12 -m venv venv
```

(Mac/Linux: `python3 -m venv venv`)

### 2. Activate it

**Windows (Git Bash, standard python.org install):**
```bash
source venv/Scripts/activate
```

**Windows (MSYS2 Python) or Mac/Linux:**
```bash
source venv/bin/activate
```

You'll know it worked when your terminal prompt shows `(venv)` at the start.

⚠️ **This does not persist across terminal windows or sessions.** Every time you open a new terminal to work in `backend/`, you must reactivate it before running any Python command — if you see `command not found` for something you know is installed (like `uvicorn`), this is almost always why.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Running the Server

To let your phone (on the same wifi network) connect to this server for testing, bind to `0.0.0.0`, not just localhost:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- Local test: http://127.0.0.1:8000
- Interactive API docs (Swagger UI): http://127.0.0.1:8000/docs
- From your phone: `http://YOUR-LOCAL-IP:8000` — find your IP with `ipconfig` (Windows) and look for "IPv4 Address" under your active wifi adapter

**Note:** if you install any new package, re-freeze dependencies so teammates stay in sync:
```bash
pip freeze > requirements.txt
```

## Project Structure