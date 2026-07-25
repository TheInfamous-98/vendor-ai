"""
Item Service - Handles all business logic for inventory items.

This service provides functions for:
- Creating items
- Updating items
- Deleting items
- Getting items with stock status
"""

from sqlalchemy.orm import Session
from database import Item, HistoricalDemand


def get_all_items(db: Session):
    """
    Get all items with stock status.

    Args:
        db: Database session

    Returns:
        list: List of items with status and alert information
    """
    items = db.query(Item).all()
    result = []

    for item in items:
        if item.stock < 10:
            status = "low_stock"
            alert = f"Low stock! Current: {item.stock}"
        elif item.stock > 100:
            status = "overstocked"
            alert = f"Overstocked! Consider reducing order"
        else:
            status = "adequate"
            alert = None

        result.append({
            "id": item.id,
            "name": item.name,
            "stock": item.stock,
            "price": item.price,
            "status": status,
            "alert": alert
        })

    return result


def get_item_by_id(db: Session, item_id: int):
    """
    Get a single item by ID.

    Args:
        db: Database session
        item_id: Item ID

    Returns:
        Item object or None
    """
    return db.query(Item).filter(Item.id == item_id).first()


def create_item(db: Session, name: str, stock: int, price: float):
    """
    Create a new item.

    Args:
        db: Database session
        name: Item name
        stock: Initial stock level
        price: Item price

    Returns:
        Item object that was created
    """
    new_item = Item(
        name=name,
        stock=stock,
        price=price
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


def update_item(db: Session, item_id: int, name: str = None, stock: int = None, price: float = None):
    """
    Update an existing item.

    Args:
        db: Database session
        item_id: Item ID to update
        name: New name (optional)
        stock: New stock level (optional)
        price: New price (optional)

    Returns:
        Updated item object or None if not found
    """
    item = db.query(Item).filter(Item.id == item_id).first()

    if not item:
        return None

    if name is not None:
        item.name = name
    if stock is not None:
        item.stock = stock
    if price is not None:
        item.price = price

    db.commit()
    db.refresh(item)
    return item


def delete_item(db: Session, item_id: int):
    """
    Delete an item.

    Args:
        db: Database session
        item_id: Item ID to delete

    Returns:
        True if deleted, False if not found
    """
    item = db.query(Item).filter(Item.id == item_id).first()

    if not item:
        return False

    db.delete(item)
    db.commit()
    return True


def get_items_summary(db: Session):
    """
    Get summary statistics for all items.

    Args:
        db: Database session

    Returns:
        dict: Summary statistics
    """
    items = db.query(Item).all()

    total_items = len(items)
    total_stock = sum(item.stock for item in items)
    total_value = sum(item.stock * item.price for item in items)
    low_stock_count = sum(1 for item in items if item.stock < 10)

    return {
        "total_items": total_items,
        "total_stock": total_stock,
        "total_inventory_value": round(total_value, 2),
        "low_stock_items": low_stock_count
    }
