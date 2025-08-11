from django.shortcuts import get_object_or_404
from ninja import Router
from .models import Expense, Category
from .schema import ExpenseIn, ExpenseOut
from users.auth import JWTAuth

auth = JWTAuth()
expense_router = Router(tags=["Expenses"])


# Create Expense
@expense_router.post("/", response=ExpenseOut, auth=auth)
def create_expense(request, payload: ExpenseIn):
    category = None

    if payload.category_id:
        category = get_object_or_404(Category, id=payload.category_id, user=request.auth)

    expense = Expense.objects.create(
        user=request.auth,
        category=category,
        amount=payload.amount,
        description=payload.description or "",
        date=payload.date or None
    )
    return expense


# List all Expenses (with optional filters)
@expense_router.get("/", response=list[ExpenseOut], auth=auth)
def list_expenses(
    request,
    category_id: int | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    search: str | None = None
):
    qs = Expense.objects.filter(user=request.auth)

    if category_id:
        qs = qs.filter(category_id=category_id)
    if start_date and end_date:
        qs = qs.filter(date__range=[start_date, end_date]) 
    if search:
        qs = qs.filter(description__icontains=search)

    return qs


# Get single Expense
@expense_router.get("/{expense_id}", response=ExpenseOut, auth=auth)
def get_expense(request, expense_id: int):
    return get_object_or_404(Expense, id=expense_id, user=request.auth)


# Update Expense
@expense_router.put("/{expense_id}", response=ExpenseOut, auth=auth)
def update_expense(request, expense_id: int, payload: ExpenseIn):
    expense = get_object_or_404(Expense, id=expense_id, user=request.auth)

    category = None
    if payload.category_id:
        category = get_object_or_404(Category, id=payload.category_id, user=request.auth)

    expense.category = category
    expense.amount = payload.amount
    expense.description = payload.description or ""
    expense.date = payload.date or expense.date
    expense.save()    

    return expense


# Delete Expense
@expense_router.delete("/{expense_id}", auth=auth)
def delete_expense(request, expense_id: int):
    expense = get_object_or_404(Expense, id=expense_id, user=request.auth)
    expense.delete()
    return {"success": True}

