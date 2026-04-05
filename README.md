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

> **macOS note**: Docker requires [Docker Desktop](https://www.docker.com/products/docker-desktop). Install it, then launch the app and wait for the menu bar icon to become active before running the command above.

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
python3.11 -m venv .venv
source .venv/bin/activate
```

> **macOS note**: macOS ships with Python 3.9, which does not meet the `>=3.11` requirement. Install a newer version first: `brew install python@3.11`

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -e ".[dev]"
```

> Upgrading pip is required on older installations — pip 21.3+ is needed for editable installs with the `hatchling` build backend.

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit the `.env` file and fill in the values described in the sections below. The database URL works with the Docker Compose setup out of the box; JWT and OAuth keys require generation or registration steps.

> Make sure `.env` is created inside the `backlogstats-backend/` directory (where `alembic.ini` lives), not the repo root.

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

## Authentication setup

### JWT secret key

Generate a random 32-byte secret and add it to your `.env`:

```bash
openssl rand -hex 32
```

```
JWT_SECRET_KEY=<output from above>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=30
```

`JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, and `REFRESH_TOKEN_EXPIRE_DAYS` have sensible defaults in `.env.example` and rarely need changing locally.

The server starts without a `JWT_SECRET_KEY`, but all auth endpoints will return tokens signed with an empty string — **always set this in staging and production**.

### Auth endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/auth/register` | Register with email + password, returns token pair |
| `POST` | `/api/v1/auth/login` | Login with email + password, returns token pair |
| `POST` | `/api/v1/auth/refresh` | Exchange a refresh token for a new token pair |
| `POST` | `/api/v1/auth/google` | Exchange a Google authorization code for a token pair |
| `POST` | `/api/v1/auth/discord` | Exchange a Discord authorization code for a token pair |

Protected endpoints expect an `Authorization: Bearer <access_token>` header.

### Google OAuth2 setup

Required only if you want to test Google Sign-In locally. The server starts without these values; `POST /api/v1/auth/google` returns **400 Bad Request** if they are not set.

1. Go to [console.cloud.google.com](https://console.cloud.google.com) and create (or select) a project.
2. Navigate to **APIs & Services** → **Credentials** → **Create Credentials** → **OAuth client ID**.
3. Set application type to **Web application**.
4. Add your frontend's origin to **Authorized JavaScript origins** and its callback URL to **Authorized redirect URIs**.
5. Copy the **Client ID** and **Client Secret**.
6. Add them to your `.env`:

```
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
```

The backend receives a `{ code, redirect_uri }` from the frontend, exchanges it with Google's token endpoint, verifies the returned ID token against Google's public JWKS, and returns a Backlogstats token pair.

### Discord OAuth2 setup

Required only if you want to test Discord Sign-In locally. The server starts without these values; `POST /api/v1/auth/discord` returns **400 Bad Request** if they are not set.

1. Go to [discord.com/developers/applications](https://discord.com/developers/applications) and click **New Application**.
2. Open the **OAuth2** tab.
3. Add your frontend's callback URL to **Redirects**.
4. Copy the **Client ID** and **Client Secret** from the top of the OAuth2 tab.
5. Add them to your `.env`:

```
DISCORD_CLIENT_ID=your_client_id_here
DISCORD_CLIENT_SECRET=your_client_secret_here
```

The frontend must request the `identify` and `email` scopes when initiating the OAuth2 flow — Discord only returns an email address when the `email` scope is present. The backend exchanges the code, fetches the user from `GET /users/@me`, and returns a Backlogstats token pair.

> **Apple Sign In** — required before App Store submission if any other social login is present. Implementation is deferred (needs Apple Developer account + different JWKS verification flow). The `apple_id` column already exists on the `User` model.
>
> **Steam OpenID** — uses OpenID 2.0, not OAuth2. Deferred to a separate task. The `steam_id` column already exists on the `User` model.

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
