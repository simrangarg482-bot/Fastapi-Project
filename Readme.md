# Car Price Prediction API

A FastAPI service that predicts used-car selling prices with a trained
scikit-learn model, wrapped with the pieces a real deployment needs:
JWT auth, an API key check, Redis-backed response caching, Prometheus
metrics, structured logging, and centralized error handling.

## Architecture

```
Client
  │
  ├── POST /login ──────────────► JWT issued (in-memory user store)
  │
  └── POST /predict  (headers: token, api_key)
          │
          ▼
   FastAPI (app/main.py)
          │
          ├── LoggingMiddleware        (logs method/path/status)
          ├── get_current_user()       (verifies JWT)
          ├── get_api_key()            (verifies API key header)
          │
          ▼
   model_service.predict_car_price()
          │
          ├── Redis cache lookup ──── hit ──► return cached price
          │       │
          │      miss
          │       ▼
          ├── sklearn Pipeline (app/models/model.joblib)
          │     ColumnTransformer(impute, scale, one-hot) → RandomForestRegressor
          │       │
          │       ▼
          └── cache result, return prediction

   Prometheus scrapes /metrics ──► Grafana dashboards
```

## Features

- **Auth**: `/login` issues a JWT; `/predict` requires both a valid JWT
  (`token` header) and a static API key (`api_key` header)
- **ML pipeline**: numeric imputation + scaling, categorical imputation +
  one-hot encoding, fed into a `RandomForestRegressor`, trained in
  `training/train_model.py` and served via `joblib`
- **Caching**: predictions are cached in Redis, keyed by input, so
  identical requests skip the model entirely
- **Observability**: `prometheus-fastapi-instrumentator` exposes `/metrics`;
  `docker-compose` also spins up Prometheus + Grafana
- **Error handling**: a global exception handler returns a consistent
  JSON error shape instead of leaking stack traces
- **Deployment**: Dockerfile + `docker-compose.yml` for local multi-service
  runs, `render.yaml` for a one-click deploy to Render

## API endpoints

| Method | Path       | Auth required          | Description                       |
|--------|------------|-------------------------|-----------------------------------|
| POST   | `/login`   | none                     | Exchange username/password for a JWT |
| POST   | `/predict` | JWT + API key headers    | Predict a car's selling price     |
| GET    | `/metrics` | none                     | Prometheus metrics                |
| GET    | `/docs`    | none                     | Interactive Swagger UI            |

### Example: login

```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "<ADMIN_PASSWORD from your .env>"}'
```

### Example: predict

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -H "token: <access_token from /login>" \
  -H "api_key: <API_KEY from your .env>" \
  -d '{
        "company": "Maruti",
        "year": 2015,
        "owner": "First Owner",
        "fuel": "Petrol",
        "seller_type": "Individual",
        "transmission": "Manual",
        "km_driven": 45000,
        "mileage_mpg": 21.5,
        "engine_cc": 1197,
        "max_power_bhp": 82,
        "torque_nm": 113,
        "seats": 5
      }'
```

## Running locally

### 1. Configure environment variables

```bash
cp .env.example .env
# then edit .env with real values for API_KEY, JWT_SECRET_KEY, ADMIN_PASSWORD
```

### 2. Option A — plain Python

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You'll also need a local Redis instance running (`redis-server`, or via Docker:
`docker run -p 6379:6379 redis:alpine`).

### 2. Option B — Docker Compose (recommended)

Spins up the API, Redis, Prometheus, and Grafana together:

```bash
docker-compose up --build
```

- API: http://localhost:8000/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (default login `admin` / `admin` on first run)

### 3. Retrain the model (optional)

```bash
python -m training.train_model
```

Reads `data/car-details.csv`, trains the pipeline, and writes
`app/models/model.joblib`.

## Known limitations / next steps

- User store is in-memory (`app/core/users.py`) rather than a real
  database — fine for a demo, not for multi-user production use
- No automated test suite yet
- Cache keys are built from raw input values; for a larger feature set,
  hashing the input would be more robust than string concatenation

## Tech stack

FastAPI · scikit-learn · pandas · Redis · Prometheus · Grafana · Docker ·
python-jose (JWT) · passlib (password hashing)
