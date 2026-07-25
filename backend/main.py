"""
Main FastAPI Application for Smart Inventory Management System

This backend provides:
1. Basic inventory operations (CRUD)
2. ML-based demand forecasting
3. Inventory optimization recommendations
4. AI chat assistant

Structure:
- controllers/ - HTTP request handlers
- services/ - Business logic
- utils/ - Helper functions
- database.py - Database models and session
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from database import SessionLocal, Item, HistoricalDemand
from ai import ask_ai

app = FastAPI(title="Smart Inventory API", version="2.0")

# Enable frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# HOME ROUTE
# ============================================

@app.get("/")
def home():
    """API status check"""
    return {
        "message": "Smart Inventory API Running",
        "version": "2.0",
        "endpoints": {
            "inventory": ["/items", "/add-item", "/update-item", "/delete-item"],
            "ml": ["/predict-demand", "/optimize-inventory", "/generate-sample-data"],
            "ai": ["/ask-ai"]
        }
    }


# ============================================
# INVENTORY ENDPOINTS
# ============================================

@app.get("/items")
def get_items():
    """Get all items with stock status"""
    db = SessionLocal()
    try:
        # Import here to avoid circular imports
        from services.item_service import get_all_items
        return get_all_items(db)
    finally:
        db.close()


@app.post("/add-item")
async def add_item(request: Request):
    """Add a new item to inventory"""
    data = await request.json()

    db = SessionLocal()
    try:
        from services.item_service import create_item
        item = create_item(
            db=db,
            name=data["name"],
            stock=data["stock"],
            price=data["price"]
        )
        return {
            "message": "Item Added Successfully",
            "item": {"id": item.id, "name": item.name, "stock": item.stock}
        }
    finally:
        db.close()


@app.put("/update-item/{item_id}")
async def update_item(item_id: int, request: Request):
    """Update existing item"""
    data = await request.json()

    db = SessionLocal()
    try:
        from services.item_service import update_item
        item = update_item(
            db=db,
            item_id=item_id,
            name=data.get("name"),
            stock=data.get("stock"),
            price=data.get("price")
        )
        if not item:
            return {"error": "Item not found"}
        return {
            "message": "Item Updated Successfully",
            "item": {"id": item.id, "name": item.name}
        }
    finally:
        db.close()


@app.delete("/delete-item/{item_id}")
def delete_item(item_id: int):
    """Delete an item from inventory"""
    db = SessionLocal()
    try:
        from services.item_service import delete_item
        deleted = delete_item(db=db, item_id=item_id)
        if not deleted:
            return {"error": "Item not found"}
        return {"message": "Item Deleted Successfully", "item_id": item_id}
    finally:
        db.close()


# ============================================
# ML ENDPOINTS - DEMAND FORECASTING
# ============================================

@app.get("/generate-sample-data")
def generate_sample_data_endpoint():
    """
    Generate and save sample historical demand data.
    This is used when you don't have real historical data.
    """
    db = SessionLocal()
    try:
        from services.ml_service import generate_sample_data
        from database import HistoricalDemand

        # Generate sample data
        sample_data = generate_sample_data()

        # Save to database
        records_created = 0
        for record in sample_data:
            exists = db.query(HistoricalDemand).filter(
                HistoricalDemand.date == record["date"],
                HistoricalDemand.item_name == record["item_name"]
            ).first()

            if not exists:
                record_obj = HistoricalDemand(
                    date=record["date"],
                    item_name=record["item_name"],
                    demand=record["demand"],
                    day_of_week=record["day_of_week"]
                )
                db.add(record_obj)
                records_created += 1

        db.commit()

        return {
            "message": "Sample data generated and saved",
            "records_count": records_created
        }
    finally:
        db.close()


@app.get("/predict-demand")
def predict_demand_endpoint(days: int = 7):
    """
    Predict demand for all items using ML.

    Args:
        days: Number of days to predict (default: 7)

    Returns:
        List of predictions for each item including:
        - Slope (trend direction)
        - Intercept (baseline demand)
        - Predicted demand per day
        - Trend classification
    """
    db = SessionLocal()
    try:
        from services.ml_service import predict_all_items

        # Get historical data
        historical_data = db.query(HistoricalDemand).all()

        if not historical_data:
            # Generate sample data if none exists
            from services.ml_service import generate_sample_data

            sample_data = generate_sample_data()
            for record in sample_data:
                record_obj = HistoricalDemand(
                    date=record["date"],
                    item_name=record["item_name"],
                    demand=record["demand"],
                    day_of_week=record["day_of_week"]
                )
                db.add(record_obj)
            db.commit()
            historical_data = db.query(HistoricalDemand).all()

        # Convert to list of dicts for ML service
        historical_list = [
            {
                "date": h.date.strftime("%Y-%m-%d") if hasattr(h, 'date') else str(h.date),
                "item_name": h.item_name,
                "demand": h.demand,
                "day_of_week": h.day_of_week
            }
            for h in historical_data
        ]

        # Make predictions
        predictions = predict_all_items(historical_list, days_to_predict=days)

        return {
            "message": "Demand Predictions",
            "days_predicted": days,
            "predictions": predictions
        }
    finally:
        db.close()


# ============================================
# ML ENDPOINTS - OPTIMIZATION
# ============================================

@app.get("/optimize-inventory")
def optimize_inventory_endpoint():
    """
    Optimize inventory levels for all items.

    Calculates:
    - Optimal stock level to minimize total cost
    - Safety stock recommendations
    - Reorder suggestions

    Returns:
        Optimization recommendations for each item
    """
    db = SessionLocal()
    try:
        from services.ml_service import optimize_inventory

        # Get items from database
        items = db.query(Item).all()
        items_data = [
            {"name": item.name, "stock": item.stock, "price": item.price}
            for item in items
        ]

        # Get historical data
        historical_data = db.query(HistoricalDemand).all()

        if not historical_data:
            return {
                "error": "No historical data. Call /generate-sample-data first."
            }

        # Convert to list of dicts
        historical_list = [
            {
                "date": h.date.strftime("%Y-%m-%d"),
                "item_name": h.item_name,
                "demand": h.demand,
                "day_of_week": h.day_of_week
            }
            for h in historical_data
        ]

        # Run optimization
        results = optimize_inventory(historical_list, items_data)

        return {
            "message": "Inventory Optimization Results",
            "items": results["items"]
        }
    finally:
        db.close()


# ============================================
# AI CHAT ENDPOINT
# ============================================

@app.post("/ask-ai")
async def ai_chat(request: Request):
    """
    Ask AI questions about your inventory.

    The AI has access to your current inventory data.
    """
    try:
        data = await request.json()
        user_question = data["question"]

        db = SessionLocal()
        items = db.query(Item).all()
        db.close()

        inventory_text = "\n".join(
            [f"{item.name}: stock {item.stock}, price {item.price}" for item in items]
        )

        prompt = f"""
You are an inventory assistant.

Inventory:
{inventory_text}

Question:
{user_question}

Answer briefly and helpfully.
"""
        answer = ask_ai(prompt)

        return {"reply": answer}

    except Exception as e:
        return {"reply": f"Error: {str(e)}"}


# ============================================
# DASHBOARD DATA (COMBINED ENDPOINT)
# ============================================

@app.get("/dashboard-data")
def get_dashboard_data():
    """
    Get all data needed for the dashboard in one call.
    This reduces multiple API calls from the frontend.
    """
    db = SessionLocal()
    try:
        # Get items
        items = db.query(Item).all()
        items_data = [
            {"id": item.id, "name": item.name, "stock": item.stock, "price": item.price}
            for item in items
        ]

        # Get historical data
        historical_data = db.query(HistoricalDemand).all()
        historical_list = [
            {
                "date": h.date.strftime("%Y-%m-%d"),
                "item_name": h.item_name,
                "demand": h.demand
            }
            for h in historical_data
        ]

        # Generate predictions if we have data
        predictions = []
        if historical_list:
            from services.ml_service import predict_all_items
            predictions = predict_all_items(historical_list, days=7)

        # Calculate summary stats
        total_items = len(items_data)
        total_stock = sum(item["stock"] for item in items_data)
        low_stock_items = [item for item in items_data if item["stock"] < 10]

        return {
            "summary": {
                "total_items": total_items,
                "total_stock": total_stock,
                "low_stock_alerts": len(low_stock_items)
            },
            "items": items_data,
            "predictions": predictions
        }
    finally:
        db.close()
