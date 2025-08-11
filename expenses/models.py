from django.db import models
from django.contrib.auth.models import User


# Category Model
class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=50)
    budget = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        help_text="Monthly budget limit for this category"
    )

    class Meta:
        unique_together = ('user', 'name')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.user.username})" 


# Expense Model
class Expense(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='expenses'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='expenses'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        category_name = self.category.name if self.category else "Uncategorized"
        return f"{self.user.username} spent {self.amount} on {category_name} at {self.date}"