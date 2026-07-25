"""
ML Service for Demand Forecasting and Inventory Optimization

This module provides:
1. Demand Forecasting - Uses Linear Regression to predict future demand
2. Sample Data Generation - Creates realistic historical sales data
3. Inventory Optimization - Recommends optimal stock levels
"""

import random
from datetime import datetime, timedelta


# ============================================
# PART 1: SAMPLE DATA GENERATION
# ============================================

def generate_sample_data():
    """
    Generate realistic sample historical sales data.
    Since we don't have real historical data, we create simulated data
    that follows realistic patterns:
    - Weekly seasonality (more sales on weekends)
    - Trend over time (growth or decline)
    - Random noise
    """
    items = ["Rice", "Wheat", "Sugar", "Oil", "Flour", "Salt", "Pulses", "Spices"]

    # Base demand for each item (items per day)
    base_demand = {
        "Rice": 25,
        "Wheat": 20,
        "Sugar": 15,
        "Oil": 12,
        "Flour": 18,
        "Salt": 10,
        "Pulses": 8,
        "Spices": 5
    }

    # Generate 90 days of historical data
    historical_data = []
    start_date = datetime.now() - timedelta(days=90)

    for day in range(90):
        current_date = start_date + timedelta(days=day)
        day_of_week = current_date.weekday()  # 0=Monday, 6=Sunday

        # Weekend effect: higher demand on weekends
        weekend_multiplier = 1.3 if day_of_week >= 5 else 1.0

        for item in items:
            # Base demand with weekly seasonality and random noise
            noise = random.uniform(0.7, 1.3)  # Random variation
            daily_demand = int(
                base_demand[item] * weekend_multiplier * noise
            )

            historical_data.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "item_name": item,
                "demand": daily_demand,
                "day_of_week": day_of_week
            })

    return historical_data


# ============================================
# PART 2: DEMAND FORECASTING (Linear Regression)
# ============================================

def simple_linear_regression(x_values, y_values):
    """
    Simple Linear Regression implementation from scratch.

    Fits a line: y = mx + c

    Args:
        x_values: List of x values (days)
        y_values: List of y values (demand)

    Returns:
        tuple: (slope, intercept)
    """
    n = len(x_values)

    if n < 2:
        return 0, sum(y_values) / len(y_values) if y_values else 0

    # Calculate means
    x_mean = sum(x_values) / n
    y_mean = sum(y_values) / n

    # Calculate slope (m) and intercept (c)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
    denominator = sum((x - x_mean) ** 2 for x in x_values)

    if denominator == 0:
        return 0, y_mean

    slope = numerator / denominator
    intercept = y_mean - (slope * x_mean)

    return slope, intercept


def predict_demand_for_item(historical_data, item_name, days_to_predict=7):
    """
    Predict future demand for a specific item using linear regression.

    Args:
        historical_data: List of historical sales records
        item_name: Name of the item to predict
        days_to_predict: Number of days into the future to predict

    Returns:
        dict: Prediction results including slope, intercept, and forecasted values
    """
    # Filter data for this item
    item_data = [d for d in historical_data if d["item_name"] == item_name]

    if not item_data:
        return {
            "item_name": item_name,
            "error": "No historical data found for this item"
        }

    # Sort by date
    item_data.sort(key=lambda x: x["date"])

    # Prepare data for regression (x = day number, y = demand)
    x_values = list(range(len(item_data)))
    y_values = [d["demand"] for d in item_data]

    # Calculate linear regression
    slope, intercept = simple_linear_regression(x_values, y_values)

    # Generate predictions
    predictions = []
    last_day = len(item_data)

    for day in range(days_to_predict):
        future_day = last_day + day
        predicted_demand = max(0, int(slope * future_day + intercept))

        # Add weekend adjustment
        day_of_week = (last_day + day) % 7
        weekend_mult = 1.3 if day_of_week >= 5 else 1.0
        predicted_demand = int(predicted_demand * weekend_mult)

        predictions.append({
            "day": day + 1,
            "predicted_demand": predicted_demand
        })

    # Calculate average demand for the prediction period
    avg_demand = sum(p["predicted_demand"] for p in predictions) / len(predictions) if predictions else 0

    return {
        "item_name": item_name,
        "slope": round(slope, 4),  # Trend direction and strength
        "intercept": round(intercept, 2),
        "average_predicted_demand": round(avg_demand, 2),
        "predictions": predictions,
        "trend": "increasing" if slope > 0.5 else "decreasing" if slope < -0.5 else "stable"
    }


def predict_all_items(historical_data, days_to_predict=7):
    """
    Predict demand for all items.

    Args:
        historical_data: List of historical sales records
        days_to_predict: Number of days to predict

    Returns:
        list: Predictions for all items
    """
    # Get unique items
    items = list(set(d["item_name"] for d in historical_data))

    predictions = []
    for item in items:
        pred = predict_demand_for_item(historical_data, item, days_to_predict)
        predictions.append(pred)

    return predictions


# ============================================
# PART 3: INVENTORY OPTIMIZATION
# ============================================

def calculate_optimal_stock(predicted_demand, current_stock, holding_cost_per_unit=1.5, shortage_cost_per_unit=5.0):
    """
    Calculate optimal stock level that minimizes total cost.

    Total Cost = Holding Cost + Shortage Cost

    Args:
        predicted_demand: Predicted demand (average for period)
        current_stock: Current stock level
        holding_cost_per_unit: Cost to hold one unit in stock
        shortage_cost_per_unit: Cost of one unit shortage (lost sales)

    Returns:
        dict: Optimal stock level and recommendations
    """
    # Optimal stock = predicted demand + safety stock
    # Safety stock covers demand variability
    safety_stock = int(predicted_demand * 0.2)  # 20% safety margin

    optimal_stock = predicted_demand + safety_stock

    # Calculate costs for different stock levels
    stock_levels = [int(optimal_stock * 0.8), int(optimal_stock), int(optimal_stock * 1.2)]

    results = []
    for stock in stock_levels:
        holding_cost = (stock - predicted_demand) * holding_cost_per_unit if stock > predicted_demand else 0
        shortage_cost = (predicted_demand - stock) * shortage_cost_per_unit if predicted_demand > stock else 0
        total_cost = holding_cost + shortage_cost

        results.append({
            "stock_level": stock,
            "holding_cost": round(holding_cost, 2),
            "shortage_cost": round(shortage_cost, 2),
            "total_cost": round(total_cost, 2)
        })

    # Find optimal
    optimal_result = min(results, key=lambda x: x["total_cost"])

    # Generate recommendation
    if current_stock < optimal_result["stock_level"]:
        recommendation = "REORDER" if optimal_result["total_cost"] < current_stock * holding_cost_per_unit else "MONITOR"
    else:
        recommendation = "OVERSTOCKED" if current_stock > optimal_stock * 1.3 else "ADEQUATE"

    return {
        "predicted_demand": predicted_demand,
        "current_stock": current_stock,
        "optimal_stock_level": optimal_result["stock_level"],
        "safety_stock": safety_stock,
        "recommendation": recommendation,
        "cost_analysis": results
    }


def optimize_inventory(historical_data, items_db):
    """
    Optimize inventory for all items.

    Args:
        historical_data: List of historical sales records
        items_db: List of items from database with current stock

    Returns:
        dict: Optimization results for all items
    """
    # Predict demand for all items
    predictions = predict_all_items(historical_data, days_to_predict=7)

    # Create lookup for current stock
    stock_lookup = {item["name"]: item["stock"] for item in items_db}

    # Optimize each item
    results = []
    for pred in predictions:
        item_name = pred["item_name"]
        current_stock = stock_lookup.get(item_name, 0)

        optimization = calculate_optimal_stock(
            predicted_demand=pred["average_predicted_demand"],
            current_stock=current_stock
        )

        results.append({
            "item_name": item_name,
            "prediction": pred,
            "optimization": optimization
        })

    return {"items": results}
