from django.shortcuts import get_object_or_404
from ninja import Router
from .models import Category
from .schema import CategoryIn, CategoryOut
from users.auth import JWTAuth

category_router = Router(tags=["Categories"])
auth = JWTAuth()

# Create Category
@category_router.post('/', response=CategoryOut, auth=auth)
def create_category(request, payload: CategoryIn):
    category = Category.objects.create(
        user=request.auth,
        name=payload.name,
        budget=payload.budget
    )
    return category


# List all Categories for logged-in user
@category_router.get("/", response=list[CategoryOut], auth=auth)
def list_categories(request):
    return Category.objects.filter(user=request.auth)


# Get single Category by ID
@category_router.get("/{category_id}", response=CategoryOut, auth=auth)
def get_category(request, category_id: int):
    category = get_object_or_404(Category, id=category_id, user=request.auth)
    return category


# Update Category
@category_router.put("/{category_id}", response=CategoryOut, auth=auth)
def update_category(request, category_id: int, payload: CategoryIn):
    category = get_object_or_404(Category, id=category_id, user=request.auth)
    category.name = payload.name
    category.budget = payload.budget
    category.save()
    return category


# Delete Category
@category_router.delete("/{category_id}", auth=auth)
def delete_category(request, category_id: int):
    category = get_object_or_404(Category, id=category_id, user=request.auth)
    category.delete()
    return {"success": True}



