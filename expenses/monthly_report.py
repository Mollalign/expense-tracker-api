from datetime import datetime
from django.db.models import Sum
from ninja.errors import HttpError
from .models import Category, Expense
from .schema import MonthlyReportOut, CategoryReport
from users.auth import JWTAuth 
from ninja import Router

router = Router(tags=["Monthly Report"])

@router.get("/monthly-report", response=MonthlyReportOut, auth=JWTAuth())
def monthly_report(request, year: int, month: int):
    try:
        month_start = datetime(year, month, 1)
        if month == 12:
            month_end = datetime(year + 1, 1, 1)
        else:
            month_end = datetime(year, month + 1, 1)
    except ValueError:
        raise HttpError(400, "Invalid year or month")

    # Filter expenses for the logged-in user in the given month
    expenses_qs = Expense.objects.filter(
        user=request.auth,
        date__gte=month_start,
        date__lt=month_end
    )

    total_spent = expenses_qs.aggregate(total=Sum("amount"))["total"] or 0

    # Get spending per category
    categories_data = []
    categories = Category.objects.filter(user=request.auth)

    for category in categories:
        spent = expenses_qs.filter(category=category).aggregate(total=Sum("amount"))["total"] or 0
        over_budget = False
        if category.budget and spent > category.budget:
            over_budget = True

        categories_data.append(CategoryReport(
            category_id=category.id,
            category_name=category.name,
            total_spent=spent,
            budget=category.budget,
            over_budget=over_budget
        ))

    return MonthlyReportOut(
        month=f"{year}-{month:02d}",
        total_spent=total_spent,
        categories=categories_data
    )
