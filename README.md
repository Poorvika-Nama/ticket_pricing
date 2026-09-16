# Cinema Pricing Engine

A modular cinema ticket pricing system built with **Python, FastAPI, React, TypeScript, and Vite**.

The project models the complete pricing flow for a cinema booking: seat-tier pricing, inventory validation, festival discounts, membership discounts, convenience fees, GST, and an itemized final receipt. It also includes a price-list import workflow, automated tests, and CI support.

> **Project goal:** Build a clean, testable pricing engine that keeps business rules separate from the API and frontend, making the system easy to extend and maintain.

## Features

- Seat-tier based ticket pricing
- Inventory and booking validation
- Festival flat discounts
- Membership percentage discounts with a cap
- Convenience fee calculation
- GST calculation on tickets and convenience fees
- Exact monetary calculations using paise and `Decimal`
- Itemized receipt breakdown
- FastAPI REST API
- Interactive Swagger API documentation
- CSV price-list import
- React + TypeScript frontend
- Browser persistence for imported pricing tiers
- Unit, API, and integration tests
- GitHub Actions CI across supported Python versions
- Development setup suitable for GitHub Codespaces

## Architecture

```text
                    ┌─────────────────────┐
                    │   React Frontend    │
                    │ TypeScript + Vite   │
                    └──────────┬──────────┘
                               │ /api
                               ▼
                    ┌─────────────────────┐
                    │     FastAPI API     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Pricing Engine     │
                    │  Business Rules     │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
        Validation         Discounts        Tax & Fees
              │                │                │
              └────────────────┼────────────────┘
                               ▼
                    ┌─────────────────────┐
                    │ Itemized Receipt    │
                    └─────────────────────┘
```

### Pricing flow

```text
Booking Request
      ↓
Validate quantity
      ↓
Validate seat tier
      ↓
Validate inventory
      ↓
Calculate base total
      ↓
Festival discount
      ↓
Member discount
      ↓
Convenience fee
      ↓
GST on tickets + fee
      ↓
Grand total
```

For the design decisions and reasoning behind this architecture, see [`reasoning.md`](reasoning.md).

## Project Structure

```text
cinema-pricing-engine/
├── pricing_engine/
│   ├── __init__.py
│   ├── models.py          # Domain models
│   ├── engine.py          # Core pricing and billing logic
│   ├── api.py             # FastAPI endpoints
│   └── price_import.py    # Price-list import/normalization
│
├── tests/
│   ├── test_engine.py
│   ├── test_api.py
│   └── test_integration.py
│
├── frontend/
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Application pages
│   │   ├── api.ts         # Backend API client
│   │   └── App.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── .env.example
│
├── .github/workflows/     # CI configuration
├── examples/              # Example usage
├── reasoning.md           # Engineering decisions and thought process
├── pyproject.toml         # Python package configuration
└── README.md
```

## Requirements

### Backend

- Python **3.11+**
- pip

### Frontend

- Node.js **18+** recommended
- npm

## Quick Start

The project has two parts: a **FastAPI backend** and a **React frontend**. Run them in separate terminals.

### 1. Clone the repository

```bash
git clone https://github.com/Poorvika-Nama/ticket_pricing.git
cd ticket_pricing
```

### 2. Set up the Python backend

Create and activate a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install the project and test dependencies:

```bash
python -m pip install -e ".[test]"
```

### 3. Start the backend

For local development:

```bash
python -m uvicorn pricing_engine.api:app --host 0.0.0.0 --port 8000 --reload
```

The API runs on port `8000`.

Verify that it is working:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok"}
```

### 4. Set up the frontend

Open a **second terminal**:

```bash
cd frontend
npm install
```

Start the Vite development server:

```bash
npm run dev -- --host 0.0.0.0
```

The frontend normally runs on port `5173`.

The frontend is configured to use the Vite `/api` proxy in development, which forwards requests to the FastAPI server on port `8000`.

## Running in GitHub Codespaces

The project can be run directly inside GitHub Codespaces.

### Backend terminal

From the repository root:

```bash
python -m pip install -e ".[test]"
python -m uvicorn pricing_engine.api:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend terminal

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

In the Codespaces **PORTS** panel, make sure ports `8000` and `5173` are forwarded. Open the forwarded **5173** URL to use the application.

> **Important:** Do not set `VITE_API_BASE_URL` to `http://127.0.0.1:8000` when accessing the frontend through the forwarded Codespaces URL. The development setup uses the Vite `/api` proxy so browser requests reach the backend correctly.

If you previously created `frontend/.env` with an old API URL, remove it or leave the variable empty:

```bash
cd frontend
rm -f .env
```

Then restart the Vite server.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Check API availability |
| `POST` | `/price-booking` | Calculate a booking price and return the itemized bill |
| `POST` | `/import-price-list` | Import and normalize a raw seat-class price list |

### API documentation

When the backend is running, FastAPI provides interactive documentation at:

```text
http://127.0.0.1:8000/docs
```

You can use Swagger UI to inspect and test the available endpoints.

## Frontend Routes

| Route | Purpose |
|---|---|
| `/` | Cinema booking and price calculation |
| `/import` | Price-list import |

Imported price tiers are stored in browser `localStorage` and shared with the booking screen. Since the current import API returns prices but does not provide inventory, imported tiers are initially shown with `0` available seats and remain unavailable until inventory is supplied through the backend show configuration.

## Example Pricing Result

For a booking with a base ticket total of **₹950.00**, the current example configuration produces:

```text
Base total                 ₹950.00
Festival discount           -₹20.00
Member discount             -₹93.00
                           ---------
Total after discounts       ₹837.00

Convenience fee              ₹20.00
GST on tickets              ₹150.66
GST on fee                    ₹3.60
                           ---------
Grand total                ₹1,011.26
```

The corresponding internal values are stored in paise:

```text
base_total            = 95000
festival_discount     = 2000
member_discount       = 9300
total_after_discounts = 83700
convenience_fee       = 2000
gst_on_tickets        = 15066
gst_on_fee            = 360
grand_total           = 101126
```

## Testing

Install test dependencies with:

```bash
python -m pip install -e ".[test]"
```

Run the complete test suite:

```bash
pytest
```

Run with more detailed output:

```bash
pytest -v
```

The test suite covers the pricing engine, API behavior, and end-to-end integration scenarios.

## Development Commands

### Backend

```bash
# Install dependencies
python -m pip install -e ".[test]"

# Start API
python -m uvicorn pricing_engine.api:app --host 0.0.0.0 --port 8000 --reload

# Run tests
pytest -v
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev -- --host 0.0.0.0

# Build production frontend
npm run build
```

## Engineering Principles

The implementation follows a few core principles:

- **Single source of truth:** pricing calculations happen in the backend engine.
- **Separation of concerns:** domain logic, HTTP API, and UI are kept separate.
- **Deterministic money calculations:** monetary values use integer paise and controlled decimal rounding.
- **Explicit business rules:** validation, discount ordering, fees, and taxes are represented directly in the pricing pipeline.
- **Explainable results:** the API returns an itemized receipt rather than only a final amount.
- **Testability:** business logic can be tested independently of the web interface.
- **Extensibility:** new pricing rules and interfaces can be added without rewriting the core engine.

## Future Enhancements

Potential extensions include:

- Database-backed shows and inventory
- Persistent bookings
- Authentication and user accounts
- Admin pricing management
- Additional discount and promotional rules
- Dynamic pricing based on demand
- Seat-specific pricing
- Production deployment
- Expanded observability and monitoring

## License

This project is currently intended as a learning, assessment, and portfolio project. Add a formal license here if the repository is later distributed as open-source software.
