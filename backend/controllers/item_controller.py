"""
Item Controller - Handles HTTP requests for inventory items.

Endpoints:
- GET /items - Get all items
- POST /add-item - Add new item
- PUT /update-item/{item_id} - Update item
- DELETE /delete-item/{item_id} - Delete item
"""

from fastapi import Request
from database import SessionLocal


def get_items():
    """
    Get all items with stock status.

    Returns:
        list: List of all items with status information
    """
    db = SessionLocal()
    try:
        # Import service here to avoid circular imports
        from services.item_service import get_all_items
        items = get_all_items(db)
        return items
    finally:
        db.close()


def add_item(data: dict):
    """
    Add a new item to inventory.

    Args:
        data: Dictionary with name, stock, price

    Returns:
        dict: Success message and created item info
    """
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


def update_item(item_id: int, data: dict):
    """
    Update an existing item.

    Args:
        item_id: ID of item to update
        data: Dictionary with optional name, stock, price

    Returns:
        dict: Success message and updated item info
    """
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


def delete_item(item_id: int):
    """
    Delete an item from inventory.

    Args:
        item_id: ID of item to delete

    Returns:
        dict: Success message or error
    """
    db = SessionLocal()
    try:
        from services.item_service import delete_item
        deleted = delete_item(db=db, item_id=item_id)
        if not deleted:
            return {"error": "Item not found"}
        return {"message": "Item Deleted Successfully", "item_id": item_id}
    finally:
        db.close()
