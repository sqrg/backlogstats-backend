# Backlogstats Backend

FastAPI backend for Backlogstats.

## Prerequisites

- Python 3.11+
- Docker (for the local PostgreSQL instance)

## Setup

### 1. Start the database

```bash
docker compose up -d
```

> **Linux / Fedora note**: if `docker compose` is not available, install the standalone compose and use the hyphenated form instead:
> ```bash
> sudo dnf install docker-compose   # Fedora
> docker-compose up -d
> ```
>
> If you get a permission denied error on the Docker socket, add your user to the `docker` group and re-apply it:
> ```bash
> sudo systemctl start docker       # start the daemon if it isn't running
> sudo systemctl enable docker      # optional: start on boot
> sudo usermod -aG docker $USER
> newgrp docker
> docker-compose up -d
> ```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -e ".[dev]"
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

The `.env` file is pre-filled for local development and works with the Docker Compose database out of the box. Edit it if your setup differs.

### 5. Run migrations

```bash
alembic upgrade head
```

### 6. (Optional) Seed the database

```bash
seed
```

## Running the development server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

Interactive docs: `http://localhost:8000/docs`

Health check: `http://localhost:8000/health`

## Code quality

Linting and formatting use [ruff](https://docs.astral.sh/ruff/).

```bash
ruff check .
ruff format .
```

Install pre-commit hooks to run these automatically on every commit:

```bash
pre-commit install
```

## IGDB setup

Game search and import require a Twitch developer account and a registered application.

1. Go to [dev.twitch.tv](https://dev.twitch.tv) and log in with a Twitch account.
2. Click **Your Console** → **Applications** → **Register Your Application**.
3. Set any name, OAuth redirect URL (`http://localhost` is fine for local use), and category.
4. Copy the **Client ID** and generate a **Client Secret**.
5. Add them to your `.env`:

```
IGDB_CLIENT_ID=your_client_id_here
IGDB_CLIENT_SECRET=your_client_secret_here
```

Without these values the server starts normally, but `GET /api/v1/games/search` and `POST /api/v1/games/from-igdb` return **503 Service Unavailable**.

Tokens expire after ~60 days and are refreshed automatically on the next request after expiry.

## Troubleshooting

**`ImportError: email-validator is not installed`** when starting the server — the `pydantic[email]` extra is missing from the virtual environment. Re-run the install step:

```bash
pip install -e ".[dev]"
```
