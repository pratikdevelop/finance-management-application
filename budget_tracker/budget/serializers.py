from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Category, Transaction, Budget, UserProfile, Currency,
    RecurringTransaction, BillReminder, SharedAccount, SharedAccountMember,
    FinancialGoal, Investment
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['id', 'code', 'name', 'symbol']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'type']
        
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class TransactionSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    category_type = serializers.ReadOnlyField(source='category.type')
    currency_code = serializers.ReadOnlyField(source='currency.code')
    receipt_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'amount', 'category', 'category_name', 'category_type', 
            'description', 'date', 'currency', 'currency_code', 
            'amount_in_base_currency', 'receipt_image', 'receipt_image_url',
            'recurring_transaction', 'shared_account', 'created_at', 'updated_at'
        ]
        
    def get_receipt_image_url(self, obj):
        if obj.receipt_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.receipt_image.url)
        return None
        
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class RecurringTransactionSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    currency_code = serializers.ReadOnlyField(source='currency.code')
    next_occurrence = serializers.DateField(read_only=True)
    
    class Meta:
        model = RecurringTransaction
        fields = [
            'id', 'amount', 'category', 'category_name', 'description',
            'frequency', 'start_date', 'end_date', 'next_occurrence',
            'is_active', 'currency', 'currency_code', 'created_at', 'updated_at'
        ]
        
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class RecurringTransactionSummarySerializer(serializers.Serializer):
    total_active = serializers.IntegerField()
    monthly_total = serializers.DecimalField(max_digits=10, decimal_places=2)
    next_7_days = serializers.IntegerField()
    all_transactions = serializers.IntegerField()

class BudgetSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    currency_code = serializers.ReadOnlyField(source='currency.code')
    
    class Meta:
        model = Budget
        fields = ['id', 'category', 'category_name', 'amount', 'month', 'year', 'currency', 'currency_code']
        
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class BillReminderSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    days_until_due = serializers.SerializerMethodField()
    
    class Meta:
        model = BillReminder
        fields = [
            'id', 'title', 'description', 'amount', 'due_date', 'category',
            'category_name', 'recurring_transaction', 'notify_days_before',
            'is_paid', 'paid_date', 'days_until_due', 'created_at', 'updated_at'
        ]
        
    def get_days_until_due(self, obj):
        from django.utils import timezone
        delta = obj.due_date - timezone.now().date()
        return delta.days
        
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class SharedAccountMemberSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = SharedAccountMember
        fields = [
            'id', 'user', 'user_details', 'role', 'can_add_transactions',
            'can_edit_transactions', 'can_delete_transactions', 'joined_at'
        ]

class SharedAccountSerializer(serializers.ModelSerializer):
    owner_details = UserSerializer(source='owner', read_only=True)
    members_details = SharedAccountMemberSerializer(
        source='sharedaccountmember_set', many=True, read_only=True
    )
    currency_code = serializers.ReadOnlyField(source='currency.code')
    
    class Meta:
        model = SharedAccount
        fields = [
            'id', 'name', 'description', 'owner', 'owner_details',
            'members_details', 'currency', 'currency_code',
            'created_at', 'updated_at'
        ]
        
    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)

class FinancialGoalSerializer(serializers.ModelSerializer):
    currency_code = serializers.ReadOnlyField(source='currency.code')
    progress_percentage = serializers.ReadOnlyField()
    shared_account_name = serializers.ReadOnlyField(source='shared_account.name')
    
    class Meta:
        model = FinancialGoal
        fields = [
            'id', 'title', 'description', 'goal_type', 'target_amount',
            'current_amount', 'currency', 'currency_code', 'start_date',
            'target_date', 'is_completed', 'completed_date', 'progress_percentage',
            'shared_account', 'shared_account_name', 'created_at', 'updated_at'
        ]
        
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class InvestmentSerializer(serializers.ModelSerializer):
    currency_code = serializers.ReadOnlyField(source='currency.code')
    total_value = serializers.ReadOnlyField()
    total_cost = serializers.ReadOnlyField()
    profit_loss = serializers.ReadOnlyField()
    profit_loss_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = Investment
        fields = [
            'id', 'name', 'symbol', 'investment_type', 'quantity',
            'purchase_price', 'current_price', 'currency', 'currency_code',
            'purchase_date', 'notes', 'total_value', 'total_cost',
            'profit_loss', 'profit_loss_percentage', 'created_at', 'updated_at'
        ]
        
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Category, Transaction, Budget, UserProfile, Currency,
    RecurringTransaction, BillReminder, SharedAccount, SharedAccountMember,
    FinancialGoal, Investment
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['id', 'code', 'name', 'symbol']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'type']
        
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class TransactionSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    category_type = serializers.ReadOnlyField(source='category.type')
    currency_code = serializers.ReadOnlyField(source='currency.code')
    receipt_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'amount', 'category', 'category_name', 'category_type', 
            'description', 'date', 'currency', 'currency_code', 
            'amount_in_base_currency', 'receipt_image', 'receipt_image_url',
            'recurring_transaction', 'shared_account', 'created_at', 'updated_at'
        ]
        
    def get_receipt_image_url(self, obj):
        if obj.receipt_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.receipt_image.url)
        return None
        
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class RecurringTransactionSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    currency_code = serializers.ReadOnlyField(source='currency.code')
    next_occurrence = serializers.DateField(read_only=True)
    
    class Meta:
        model = RecurringTransaction
        fields = [
            'id', 'amount', 'category', 'category_name', 'description',
            'frequency', 'start_date', 'end_date', 'next_occurrence',
            'is_active', 'currency', 'currency_code', 'created_at', 'updated_at'
        ]
        
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class RecurringTransactionSummarySerializer(serializers.Serializer):
    total_active = serializers.IntegerField()
    monthly_total = serializers.DecimalField(max_digits=10, decimal_places=2)
    next_7_days = serializers.IntegerField()
    all_transactions = serializers.IntegerField()

class BudgetSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    currency_code = serializers.ReadOnlyField(source='currency.code')
    
    class Meta:
        model = Budget
        fields = ['id', 'category', 'category_name', 'amount', 'month', 'year', 'currency', 'currency_code']
        
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class BillReminderSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    days_until_due = serializers.SerializerMethodField()
    
    class Meta:
        model = BillReminder
        fields = [
            'id', 'title', 'description', 'amount', 'due_date', 'category',
            'category_name', 'recurring_transaction', 'notify_days_before',
            'is_paid', 'paid_date', 'days_until_due', 'created_at', 'updated_at'
        ]
        
    def get_days_until_due(self, obj):
        from django.utils import timezone
        delta = obj.due_date - timezone.now().date()
        return delta.days
        
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class SharedAccountMemberSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = SharedAccountMember
        fields = [
            'id', 'user', 'user_details', 'role', 'can_add_transactions',
            'can_edit_transactions', 'can_delete_transactions', 'joined_at'
        ]

class SharedAccountSerializer(serializers.ModelSerializer):
    owner_details = UserSerializer(source='owner', read_only=True)
    members_details = SharedAccountMemberSerializer(
        source='sharedaccountmember_set', many=True, read_only=True
    )
    currency_code = serializers.ReadOnlyField(source='currency.code')
    
    class Meta:
        model = SharedAccount
        fields = [
            'id', 'name', 'description', 'owner', 'owner_details',
            'members_details', 'currency', 'currency_code',
            'created_at', 'updated_at'
        ]
        
    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)

class FinancialGoalSerializer(serializers.ModelSerializer):
    currency_code = serializers.ReadOnlyField(source='currency.code')
    progress_percentage = serializers.ReadOnlyField()
    shared_account_name = serializers.ReadOnlyField(source='shared_account.name')
    
    class Meta:
        model = FinancialGoal
        fields = [
            'id', 'title', 'description', 'goal_type', 'target_amount',
            'current_amount', 'currency', 'currency_code', 'start_date',
            'target_date', 'is_completed', 'completed_date', 'progress_percentage',
            'shared_account', 'shared_account_name', 'created_at', 'updated_at'
        ]
        
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class InvestmentSerializer(serializers.ModelSerializer):
    currency_code = serializers.ReadOnlyField(source='currency.code')
    total_value = serializers.ReadOnlyField()
    total_cost = serializers.ReadOnlyField()
    profit_loss = serializers.ReadOnlyField()
    profit_loss_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = Investment
        fields = [
            'id', 'name', 'symbol', 'investment_type', 'quantity',
            'purchase_price', 'current_price', 'currency', 'currency_code',
            'purchase_date', 'notes', 'total_value', 'total_cost',
            'profit_loss', 'profit_loss_percentage', 'created_at', 'updated_at'
        ]
        
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class FinancialSummarySerializer(serializers.Serializer):
    total_income = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_transfers = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    total_investments = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    total_loans = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    total_savings = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    net_balance = serializers.DecimalField(max_digits=10, decimal_places=2)
    expenses_by_category = serializers.DictField()
    monthly_trend = serializers.ListField(child=serializers.DictField())

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    default_currency_code = serializers.ReadOnlyField(source='default_currency.code')

    class Meta:
        model = UserProfile
        fields = [
            'username', 'email', 'first_name', 'last_name', 'member_since', 
            'default_currency', 'default_currency_code', 'two_factor_enabled', 
            'email_notifications', 'push_notifications'
        ]
    
    def update(self, instance, validated_data):
        # Handle User model fields
        user_data = {}
        if 'user' in validated_data:
            user_data = validated_data.pop('user')
        
        # Update UserProfile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update User fields if present
        user = instance.user
        if 'first_name' in user_data:
            user.first_name = user_data['first_name']
        if 'last_name' in user_data:
            user.last_name = user_data['last_name']
        if user_data:
            user.save()
            
        return instance