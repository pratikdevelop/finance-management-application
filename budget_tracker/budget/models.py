from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    CATEGORY_TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]
    
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=CATEGORY_TYPE_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    
    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"
    
    class Meta:
        verbose_name_plural = "Categories"

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='transactions')
    description = models.CharField(max_length=255, blank=True)
    date = models.DateField(default=timezone.now)
    
    def __str__(self):
        return f"{self.category.name}: {self.amount} on {self.date}"

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='budgets')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.CharField(max_length=2)
    year = models.IntegerField()
    
    def __str__(self):
        return f"{self.category.name} Budget: {self.amount} for {self.month}/{self.year}"
    
    class Meta:
        unique_together = ['user', 'category', 'month', 'year']

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    member_since = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.user.username
