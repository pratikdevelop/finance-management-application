from django.contrib import admin
from .models import (
    Category, Transaction, Budget, UserProfile, FinancialRecord,
    Currency, RecurringTransaction, BillReminder, SharedAccount,
    SharedAccountMember, FinancialGoal, Investment
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'user']
    list_filter = ['type']
    search_fields = ['name', 'user__username']


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'symbol']
    search_fields = ['code', 'name']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'category', 'date', 'currency', 'created_at']
    list_filter = ['date', 'category__type', 'currency']
    search_fields = ['user__username', 'description']
    date_hierarchy = 'date'


@admin.register(RecurringTransaction)
class RecurringTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'description', 'amount', 'frequency', 'next_occurrence', 'is_active']
    list_filter = ['frequency', 'is_active']
    search_fields = ['user__username', 'description']


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'amount', 'month', 'year']
    list_filter = ['year', 'month']
    search_fields = ['user__username', 'category__name']


@admin.register(BillReminder)
class BillReminderAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'amount', 'due_date', 'is_paid']
    list_filter = ['is_paid', 'due_date']
    search_fields = ['user__username', 'title']
    date_hierarchy = 'due_date'


@admin.register(SharedAccount)
class SharedAccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'created_at']
    search_fields = ['name', 'owner__username']
    # Note: Cannot use filter_horizontal with through model
    # Members are managed via SharedAccountMember admin


@admin.register(SharedAccountMember)
class SharedAccountMemberAdmin(admin.ModelAdmin):
    list_display = ['shared_account', 'user', 'role', 'joined_at']
    list_filter = ['role']
    search_fields = ['shared_account__name', 'user__username']


@admin.register(FinancialGoal)
class FinancialGoalAdmin(admin.ModelAdmin):
    list_display = []
    list_filter = []
    search_fields = ['user__username', 'title']


@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'symbol', 'investment_type', 'quantity', 'current_price']
    list_filter = ['investment_type']
    search_fields = ['user__username', 'name', 'symbol']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'member_since', 'default_currency', 'two_factor_enabled']
    list_filter = ['two_factor_enabled', 'email_notifications']
    search_fields = ['user__username', 'user__email']


@admin.register(FinancialRecord)
class FinancialRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'record_type', 'created_at']
    list_filter = ['record_type', 'created_at']
    search_fields = ['user__username']
    date_hierarchy = 'created_at'
