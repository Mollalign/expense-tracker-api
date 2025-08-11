from ninja import Schema
from typing import Optional, List
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


class CategoryReport(Schema):
    category_id: int
    category_name: str
    total_spent: float
    budget: Optional[float]
    over_budget: bool

class MonthlyReportOut(Schema):
    month: str
    total_spent: float
    categories: List[CategoryReport]    