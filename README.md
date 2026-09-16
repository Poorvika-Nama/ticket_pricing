Cinema Pricing Engine is a Python project for building a cinema ticket pricing engine in phases, starting with a clean project skeleton and providing a foundation for adding data models, pricing calculations, and tests incrementally.

## Run the API locally

Install the project and test dependencies:

```bash
pip install -e ".[test]"
```

Start the FastAPI application with Uvicorn:

```bash
uvicorn pricing_engine.api:app --reload
```

The API is then available at `http://127.0.0.1:8000`.

Useful endpoints:
- `GET /health` — liveness check
- `POST /price-booking` — price a booking and return itemized paise/rupee amounts
- `POST /import-price-list` — clean and report a raw seat-class price list

FastAPI's interactive API documentation is available at `/docs` while the server is running.

## Run the React frontend locally

The Vite + TypeScript frontend lives in `frontend/` and expects the FastAPI server above to be running.

In a second terminal:

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Set the API base URL in `frontend/.env` with:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000
```

The Vite development server will print its local URL (normally `http://localhost:5173`). Keep the backend running with Uvicorn in the first terminal.

The frontend has two routes: `/` for booking and `/import` for CSV price-list import. Imported tiers are persisted in browser `localStorage` and shared with the booking screen; because the existing import API returns prices but does not provide inventory, imported tiers enter the booking list with `0` remaining seats and are visibly disabled until inventory is supplied by a backend show configuration.
