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
