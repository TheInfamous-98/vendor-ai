# Vendor AI Business Assistant Setup

## Frontend

```powershell
npm install
npm run dev
```

The Vite app runs at `http://127.0.0.1:5173`.

## Backend

```powershell
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

The FastAPI app runs at `http://127.0.0.1:8000`.

## Ollama

```powershell
ollama run phi3:mini
```

The backend defaults to `phi3:mini`. To use another model:

```powershell
$env:OLLAMA_MODEL="phi3"
uvicorn main:app --reload
```

## Database Migration

This project uses a safe startup migration for SQLite. On backend startup, `backend/database.py` creates the new
`sales_history` and `alerts` tables and attempts to add these columns to the existing `items` table:

- `category`
- `supplier`
- `expiry_date`
- `created_at`

If a column already exists, the migration skips it. Existing rows remain intact.

## New Endpoints

- `GET /predictions` - demand forecast, daily sales estimate, days until stockout, trend.
- `GET /alerts` - low-stock, rapid depletion, expiry, overstock, and stable alerts.
- `GET /supplier-recommendations` - ranks suppliers by cost rating, reliability, lead time, item price, and stockout risk.
- `POST /seed-demo-data?force=true` - resets and recreates the local demo inventory, suppliers, expiry dates, and sales history.
- Existing endpoints remain available: `/items`, `/add-item`, `/update-item/{id}`, `/delete-item/{id}`, `/ask-ai`, `/ai-command`.

Startup also enriches older rows with a supplier, `supplier_id`, `created_at`, and realistic `expiry_date` values when those fields are missing.
