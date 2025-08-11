from ninja import NinjaAPI
from users.api import router as users_router
from expenses.categories import category_router
from expenses.expenses import expense_router
from expenses.monthly_report import router as reports_router

api = NinjaAPI(title="Expense Tracker API")

api.add_router("/users/", users_router)
api.add_router("/categories/", category_router)
api.add_router("/expenses/", expense_router)
api.add_router("/reports/", reports_router)