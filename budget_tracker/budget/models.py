from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver

class Category(models.Model):
    CATEGORY_TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('transfer', 'Transfer'),
        ('investment', 'Investment'),
        ('loan', 'Loan'),
        ('saving', 'Saving'),
    ]
    
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=CATEGORY_TYPE_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories', null=True, blank=True)
    is_default = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"
    
    class Meta:
        verbose_name_plural = "Categories"

class Currency(models.Model):
    """Supported currencies for multi-currency support"""
    code = models.CharField(max_length=3, unique=True)  # USD, EUR, GBP, etc.
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=5)
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    class Meta:
        verbose_name_plural = "Currencies"

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='transactions')
    description = models.CharField(max_length=255, blank=True)
    date = models.DateField(default=timezone.now)
    
    # Multi-currency support
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    amount_in_base_currency = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Receipt image upload
    receipt_image = models.ImageField(upload_to='receipts/', null=True, blank=True)
    
    # Link to recurring transaction if applicable
    recurring_transaction = models.ForeignKey('RecurringTransaction', on_delete=models.SET_NULL, null=True, blank=True, related_name='generated_transactions')
    
    # Shared account support
    shared_account = models.ForeignKey('SharedAccount', on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    def __str__(self):
        return f"{self.category.name}: {self.amount} on {self.date}"
    
    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['category', 'date']),
        ]

class RecurringTransaction(models.Model):
    """Model for recurring transactions (monthly bills, salary, etc.)"""
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('biweekly', 'Bi-weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recurring_transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='recurring_transactions')
    description = models.CharField(max_length=255)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    next_occurrence = models.DateField()
    is_active = models.BooleanField(default=True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.description} - {self.get_frequency_display()}"
    
    def calculate_next_occurrence(self):
        """Calculate the next occurrence date based on frequency"""
        if self.frequency == 'daily':
            return self.next_occurrence + timedelta(days=1)
        elif self.frequency == 'weekly':
            return self.next_occurrence + timedelta(weeks=1)
        elif self.frequency == 'biweekly':
            return self.next_occurrence + timedelta(weeks=2)
        elif self.frequency == 'monthly':
            return self.next_occurrence + timedelta(days=30)
        elif self.frequency == 'quarterly':
            return self.next_occurrence + timedelta(days=90)
        elif self.frequency == 'yearly':
            return self.next_occurrence + timedelta(days=365)
        return self.next_occurrence

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='budgets')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.IntegerField()
    year = models.IntegerField()
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.category.name} Budget: {self.amount} for {self.month}/{self.year}"
    
    class Meta:
        unique_together = ['user', 'category', 'month', 'year']

class BillReminder(models.Model):
    """Model for bill reminders and notifications"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bill_reminders')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    recurring_transaction = models.ForeignKey(RecurringTransaction, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Notification settings
    notify_days_before = models.IntegerField(default=3)
    is_paid = models.BooleanField(default=False)
    paid_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - Due: {self.due_date}"
    
    class Meta:
        ordering = ['due_date']

class SharedAccount(models.Model):
    """Model for shared accounts (family accounts)"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_shared_accounts')
    members = models.ManyToManyField(User, through='SharedAccountMember', related_name='shared_accounts')
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class SharedAccountMember(models.Model):
    """Through model for shared account membership with permissions"""
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('member', 'Member'),
        ('viewer', 'Viewer'),
    ]
    
    shared_account = models.ForeignKey(SharedAccount, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    can_add_transactions = models.BooleanField(default=True)
    can_edit_transactions = models.BooleanField(default=True)
    can_delete_transactions = models.BooleanField(default=False)
    
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['shared_account', 'user']

class FinancialGoal(models.Model):
    """Model for financial goal tracking"""
    GOAL_TYPE_CHOICES = [
        ('savings', 'Savings'),
        ('debt_payoff', 'Debt Payoff'),
        ('investment', 'Investment'),
        ('purchase', 'Purchase'),
        ('emergency_fund', 'Emergency Fund'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='financial_goals')


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    member_since = models.DateField(auto_now_add=True)
    # Add any other fields you want for the UserProfile

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()
    shared_account = models.ForeignKey(SharedAccount, on_delete=models.SET_NULL, null=True, blank=True, related_name='goals')
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPE_CHOICES)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    
    start_date = models.DateField(default=timezone.now)
    target_date = models.DateField()
    is_completed = models.BooleanField(default=False)
    completed_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.current_amount}/{self.target_amount}"
    
    @property
    def progress_percentage(self):
        if self.target_amount > 0:
            return (self.current_amount / self.target_amount) * 100
        return 0
    
    class Meta:
        ordering = ['-created_at']

class Investment(models.Model):
    """Model for investment portfolio tracking"""
    INVESTMENT_TYPE_CHOICES = [
        ('stock', 'Stock'),
        ('bond', 'Bond'),
        ('mutual_fund', 'Mutual Fund'),
        ('etf', 'ETF'),
        ('crypto', 'Cryptocurrency'),
        ('real_estate', 'Real Estate'),
        ('commodity', 'Commodity'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='investments')
    name = models.CharField(max_length=200)
    symbol = models.CharField(max_length=20, blank=True)
    investment_type = models.CharField(max_length=20, choices=INVESTMENT_TYPE_CHOICES)
    
    quantity = models.DecimalField(max_digits=15, decimal_places=6)
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2)
    current_price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    
    purchase_date = models.DateField()
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.symbol})"
    
    @property
    def total_value(self):
        return self.quantity * self.current_price
    
    @property
    def total_cost(self):
        return self.quantity * self.purchase_price
    
    @property
    def profit_loss(self):
        return self.total_value - self.total_cost
    
    @property
    def profit_loss_percentage(self):
        if self.total_cost > 0:
            return ((self.total_value - self.total_cost) / self.total_cost) * 100
        return 0
    
    class Meta:
        ordering = ['-created_at']

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    member_since = models.DateField(auto_now_add=True)
    
    # Multi-currency support
    default_currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Two-factor authentication
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=32, blank=True)
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    fcm_token = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.user.username

class FinancialRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='financial_records')
    data = models.JSONField()
    record_type = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Financial Record for {self.user.username} ({self.record_type})"
