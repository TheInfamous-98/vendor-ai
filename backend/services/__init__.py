# Services module for inventory management system

from .ml_service import (
    generate_sample_data,
    simple_linear_regression,
    predict_demand_for_item,
    predict_all_items,
    calculate_optimal_stock,
    optimize_inventory
)

from .item_service import (
    get_all_items,
    get_item_by_id,
    create_item,
    update_item,
    delete_item,
    get_items_summary
)

__all__ = [
    # ML Service
    "generate_sample_data",
    "simple_linear_regression",
    "predict_demand_for_item",
    "predict_all_items",
    "calculate_optimal_stock",
    "optimize_inventory",
    # Item Service
    "get_all_items",
    "get_item_by_id",
    "create_item",
    "update_item",
    "delete_item",
    "get_items_summary",
]
