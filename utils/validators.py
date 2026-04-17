import re
from config import MAP_WIDTH, MAP_HEIGHT

def valid_coord(coord: str) -> bool:
    if not coord or len(coord) < 2:
        return False
    col = coord[0].upper()
    row = coord[1:]
    if not col.isalpha() or not row.isdigit():
        return False
    col_index = ord(col) - 65
    row_index = int(row) - 1
    return 0 <= col_index < MAP_WIDTH and 0 <= row_index < MAP_HEIGHT

def valid_resource(resource: str) -> bool:
    return resource.lower() in ("gold", "food", "materials", "influence")

def valid_treaty_type(treaty_type: str) -> bool:
    return treaty_type.lower() in ("alliance", "nap", "trade")

def valid_order_type(order_type: str) -> bool:
    return order_type.lower() in ("buy", "sell")

def valid_amount(amount: int, minimum: int = 1, maximum: int = 1_000_000) -> bool:
    return minimum <= amount <= maximum

def valid_building_name(name: str) -> bool:
    from db.queries.buildings import BUILDING_DEFINITIONS
    return name.lower() in BUILDING_DEFINITIONS

def clamp(value: int, min_val: int, max_val: int) -> int:
    return max(min_val, min(max_val, value))
