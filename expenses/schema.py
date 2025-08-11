from ninja import Schema
from typing import Optional
import datetime

# CATEGORY SCHEMAS
class CategoryIn(Schema):
    name: str
    budget: Optional[float] = None

class CategoryOut(Schema):
    id: int
    name: str
    budget: Optional[float]   

# EXPENSE SCHEMAS
class ExpenseIn(Schema):
    category_id: Optional[int] = None 
    amount: float
    description: Optional[str] = None
    date: Optional[datetime.date] = None

class ExpenseOut(Schema):
    id: int
    category: Optional[CategoryOut] = None  # Nested output for category details
    amount: float
    description: Optional[str]
    date: datetime.date  