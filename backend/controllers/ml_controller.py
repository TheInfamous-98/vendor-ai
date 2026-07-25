"""
ML Controller - Handles HTTP requests for ML-based features.

Endpoints:
- GET /generate-sample-data - Generate sample historical data
- GET /predict-demand - Predict future demand
- GET /optimize-inventory - Optimize inventory levels
"""

from database import SessionLocal


def generate_sample_data():
    """
    Generate and save sample historical demand data.

    Returns:
        dict: Success message and number of records created
    """
    db = SessionLocal()
    try:
        from services.ml_service import generate_sample_data
        from database import HistoricalDemand
        from datetime import date

        # Generate sample data
        sample_data = generate_sample_data()

        # Save to database
        records_created = 0
        for record in sample_data:
            # Check if record already exists
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


def predict_demand(days: int = 7):
    """
    Predict demand for all items using ML.

    Args:
        days: Number of days to predict

    Returns:
        dict: Predictions for all items
    """
    db = SessionLocal()
    try:
        from services.ml_service import predict_all_items
        from database import HistoricalDemand

        # Get historical data
        historical_data = db.query(HistoricalDemand).all()

        if not historical_data:
            # Generate sample data if none exists
            from services.ml_service import generate_sample_data
            from datetime import date

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


def optimize_inventory():
    """
    Optimize inventory levels for all items.

    Returns:
        dict: Optimization recommendations for all items
    """
    db = SessionLocal()
    try:
        from services.ml_service import optimize_inventory
        from database import Item

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
