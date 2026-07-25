"""
Helper functions for the inventory management system.

This module contains utility functions that are used across the application:
- Date handling
- Data validation
- Calculation helpers
"""

from datetime import datetime, timedelta


def get_date_range(days: int, include_today: bool = True):
    """
    Generate a list of dates for the given range.

    Args:
        days: Number of days to generate
        include_today: Whether to include today in the range

    Returns:
        List of date strings in YYYY-MM-DD format
    """
    dates = []
    start_date = datetime.now()

    if not include_today:
        start_date = datetime.now() - timedelta(days=1)

    for i in range(days):
        date = start_date + timedelta(days=i)
        dates.append(date.strftime("%Y-%m-%d"))

    return dates


def calculate_moving_average(data: list, window: int = 3):
    """
    Calculate moving average for a list of values.

    Args:
        data: List of numeric values
        window: Size of the moving window

    Returns:
        List of moving averages
    """
    if not data or len(data) < window:
        return data

    averages = []
    for i in range(len(data) - window + 1):
        window_data = data[i:i + window]
        avg = sum(window_data) / window
        averages.append(round(avg, 2))

    return averages


def round_number(value: float, decimals: int = 2):
    """Round a number to specified decimal places."""
    return round(value, decimals)


def safe_divide(numerator: float, denominator: float, default: float = 0):
    """
    Safely divide two numbers, returning default if denominator is zero.

    Args:
        numerator: Number to divide
        denominator: Number to divide by
        default: Value to return if denominator is zero

    Returns:
        Result of division or default value
    """
    if denominator == 0:
        return default
    return numerator / denominator


def convert_to_serializable(obj):
    """
    Convert objects to JSON-serializable format.
    Handles datetime, decimal, and other non-serializable types.
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, timedelta):
        return str(obj)
    elif isinstance(obj, float):
        return round(obj, 2)
    return obj
