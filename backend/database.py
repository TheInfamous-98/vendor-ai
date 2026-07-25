from sqlalchemy import create_engine, Column, Integer, String, Date, Float
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./inventory.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    stock = Column(Integer)
    price = Column(Float)


class HistoricalDemand(Base):
    """Stores historical sales data for ML training"""
    __tablename__ = "historical_demand"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    item_name = Column(String)
    demand = Column(Integer)
    day_of_week = Column(Integer)


Base.metadata.create_all(bind=engine)


# Helper functions
def get_items(db):
    """Get all items from database"""
    return db.query(Item).all()


def get_historical_demand(db):
    """Get all historical demand data"""
    return db.query(HistoricalDemand).all()


def save_historical_demand(db, demand_data):
    """
    Save historical demand data to database.

    Args:
        db: Database session
        demand_data: List of demand records
    """
    for record in demand_data:
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

    db.commit()


def get_items_with_stock_status(db):
    """
    Get items with stock status (low, adequate, overstocked).
    Uses simple thresholds: low < 10, overstocked > 100
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
