"""
Advanced Investment Management Models
Includes portfolio analytics, dividend tracking, asset allocation, and more
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from .models import Currency, Investment


class InvestmentDividend(models.Model):
    """Track dividend payments from investments"""
    investment = models.ForeignKey(Investment, on_delete=models.CASCADE, related_name='dividends')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField()
    ex_dividend_date = models.DateField(null=True, blank=True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    is_reinvested = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.investment.name} - ${self.amount} on {self.payment_date}"
    
    class Meta:
        ordering = ['-payment_date']


class InvestmentTransaction(models.Model):
    """Track buy/sell transactions for investments"""
    TRANSACTION_TYPE_CHOICES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
        ('dividend', 'Dividend'),
        ('split', 'Stock Split'),
        ('transfer_in', 'Transfer In'),
        ('transfer_out', 'Transfer Out'),
    ]
    
    investment = models.ForeignKey(Investment, on_delete=models.CASCADE, related_name='investment_transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    quantity = models.DecimalField(max_digits=15, decimal_places=6)
    price_per_unit = models.DecimalField(max_digits=12, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transaction_date = models.DateField()
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} {self.quantity} {self.investment.symbol}"
    
    class Meta:
        ordering = ['-transaction_date']


class PortfolioAllocation(models.Model):
    """Define target asset allocation for portfolio"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolio_allocations')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    # Target allocations (should sum to 100)
    stocks_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    bonds_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    crypto_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    real_estate_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    commodities_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    cash_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    other_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"
    
    @property
    def total_percentage(self):
        return (
            self.stocks_percentage + self.bonds_percentage + 
            self.crypto_percentage + self.real_estate_percentage +
            self.commodities_percentage + self.cash_percentage + 
            self.other_percentage
        )


class InvestmentWatchlist(models.Model):
    """Track investments user is interested in but hasn't purchased"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist')
    symbol = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    investment_type = models.CharField(max_length=20, choices=Investment.INVESTMENT_TYPE_CHOICES)
    target_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    current_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    
    # Alert settings
    alert_on_price_drop = models.BooleanField(default=False)
    alert_price_threshold = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.symbol} - {self.name}"
    
    class Meta:
        unique_together = ['user', 'symbol']
        ordering = ['-created_at']


class InvestmentPriceHistory(models.Model):
    """Store historical price data for investments"""
    investment = models.ForeignKey(Investment, on_delete=models.CASCADE, related_name='price_history', null=True, blank=True)
    watchlist_item = models.ForeignKey(InvestmentWatchlist, on_delete=models.CASCADE, related_name='price_history', null=True, blank=True)
    symbol = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    volume = models.BigIntegerField(null=True, blank=True)
    date = models.DateField()
    
    # OHLC data
    open_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    high_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    low_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    close_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.symbol} - ${self.price} on {self.date}"
    
    class Meta:
        unique_together = ['symbol', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['symbol', 'date']),
        ]


class InvestmentGoal(models.Model):
    """Specific investment goals linked to financial goals"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='investment_goals')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    target_date = models.DateField()
    
    # Risk profile
    RISK_PROFILE_CHOICES = [
        ('conservative', 'Conservative'),
        ('moderate', 'Moderate'),
        ('aggressive', 'Aggressive'),
    ]
    risk_profile = models.CharField(max_length=20, choices=RISK_PROFILE_CHOICES, default='moderate')
    
    # Expected return rate (annual percentage)
    expected_return_rate = models.DecimalField(max_digits=5, decimal_places=2, default=7.0)
    
    # Linked investments
    investments = models.ManyToManyField(Investment, related_name='goals', blank=True)
    
    is_completed = models.BooleanField(default=False)
    completed_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    @property
    def progress_percentage(self):
        if self.target_amount > 0:
            return (self.current_amount / self.target_amount) * 100
        return 0
    
    @property
    def monthly_contribution_needed(self):
        """Calculate monthly contribution needed to reach goal"""
        from datetime import date
        today = date.today()
        months_remaining = (self.target_date.year - today.year) * 12 + (self.target_date.month - today.month)
        
        if months_remaining <= 0:
            return 0
        
        remaining_amount = self.target_amount - self.current_amount
        return remaining_amount / months_remaining


class TaxLotTracking(models.Model):
    """Track tax lots for investments (FIFO, LIFO, specific identification)"""
    investment = models.ForeignKey(Investment, on_delete=models.CASCADE, related_name='tax_lots')
    purchase_date = models.DateField()
    quantity = models.DecimalField(max_digits=15, decimal_places=6)
    cost_basis_per_unit = models.DecimalField(max_digits=12, decimal_places=2)
    total_cost_basis = models.DecimalField(max_digits=12, decimal_places=2)
    remaining_quantity = models.DecimalField(max_digits=15, decimal_places=6)
    
    # For tracking sales
    is_closed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.investment.symbol} - {self.quantity} @ ${self.cost_basis_per_unit}"
    
    class Meta:
        ordering = ['purchase_date']


class PortfolioRebalanceLog(models.Model):
    """Log portfolio rebalancing activities"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rebalance_logs')
    rebalance_date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True)
    
    # Before rebalancing
    before_allocation = models.JSONField()
    
    # After rebalancing
    after_allocation = models.JSONField()
    
    # Transactions performed
    transactions_summary = models.JSONField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Rebalance on {self.rebalance_date} - {self.user.username}"
    
    class Meta:
        ordering = ['-rebalance_date']


class InvestmentAlert(models.Model):
    """Alerts for investment price movements and events"""
    ALERT_TYPE_CHOICES = [
        ('price_above', 'Price Above'),
        ('price_below', 'Price Below'),
        ('percent_gain', 'Percent Gain'),
        ('percent_loss', 'Percent Loss'),
        ('dividend_announced', 'Dividend Announced'),
        ('earnings_report', 'Earnings Report'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='investment_alerts')
    investment = models.ForeignKey(Investment, on_delete=models.CASCADE, related_name='alerts', null=True, blank=True)
    watchlist_item = models.ForeignKey(InvestmentWatchlist, on_delete=models.CASCADE, related_name='alerts', null=True, blank=True)
    
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPE_CHOICES)
    threshold_value = models.DecimalField(max_digits=12, decimal_places=2)
    is_active = models.BooleanField(default=True)
    is_triggered = models.BooleanField(default=False)
    triggered_at = models.DateTimeField(null=True, blank=True)
    
    # Notification preferences
    send_email = models.BooleanField(default=True)
    send_push = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        item_name = self.investment.name if self.investment else self.watchlist_item.name
        return f"{item_name} - {self.get_alert_type_display()}"
    
    class Meta:
        ordering = ['-created_at']


class InvestmentPerformanceSnapshot(models.Model):
    """Periodic snapshots of portfolio performance"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='performance_snapshots')
    snapshot_date = models.DateField(default=timezone.now)
    
    # Portfolio metrics
    total_value = models.DecimalField(max_digits=15, decimal_places=2)
    total_cost_basis = models.DecimalField(max_digits=15, decimal_places=2)
    total_gain_loss = models.DecimalField(max_digits=15, decimal_places=2)
    total_gain_loss_percentage = models.DecimalField(max_digits=8, decimal_places=2)
    
    # Dividend income
    total_dividend_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Asset allocation
    allocation_breakdown = models.JSONField()
    
    # Individual holdings
    holdings_detail = models.JSONField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Snapshot {self.snapshot_date} - {self.user.username}"
    
    class Meta:
        ordering = ['-snapshot_date']
        unique_together = ['user', 'snapshot_date']
