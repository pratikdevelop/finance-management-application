"""
Celery tasks for background processing
"""
from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from .models import RecurringTransaction, Transaction, BillReminder, UserProfile
from .utils.currency_utils import convert_amount


@shared_task
def process_recurring_transactions():
    """
    Process recurring transactions that are due
    """
    today = timezone.now().date()
    
    # Get all active recurring transactions that are due
    recurring_transactions = RecurringTransaction.objects.filter(
        is_active=True,
        next_occurrence__lte=today
    )
    
    processed_count = 0
    
    for recurring_trans in recurring_transactions:
        # Check if end_date has passed
        if recurring_trans.end_date and recurring_trans.end_date < today:
            recurring_trans.is_active = False
            recurring_trans.save()
            continue
        
        # Create a new transaction
        Transaction.objects.create(
            user=recurring_trans.user,
            amount=recurring_trans.amount,
            category=recurring_trans.category,
            description=recurring_trans.description,
            date=recurring_trans.next_occurrence,
            currency=recurring_trans.currency,
            recurring_transaction=recurring_trans
        )
        
        # Update next occurrence
        recurring_trans.next_occurrence = recurring_trans.calculate_next_occurrence()
        recurring_trans.save()
        
        processed_count += 1
    
    return f"Processed {processed_count} recurring transactions"


@shared_task
def send_bill_reminders():
    """
    Send reminders for upcoming bills
    """
    today = timezone.now().date()
    
    # Get all unpaid bills
    upcoming_bills = BillReminder.objects.filter(
        is_paid=False,
        due_date__gte=today
    )
    
    sent_count = 0
    
    for bill in upcoming_bills:
        days_until_due = (bill.due_date - today).days
        
        # Send reminder if within notification window
        if days_until_due <= bill.notify_days_before:
            user_profile = UserProfile.objects.get(user=bill.user)
            
            if user_profile.email_notifications:
                send_mail(
                    subject=f"Bill Reminder: {bill.title}",
                    message=f"Your bill '{bill.title}' of ${bill.amount} is due on {bill.due_date}. "
                            f"Days remaining: {days_until_due}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[bill.user.email],
                    fail_silently=True,
                )
                sent_count += 1
    
    return f"Sent {sent_count} bill reminders"


@shared_task
def update_investment_prices():
    """
    Update current prices for investments (placeholder - would integrate with real API)
    """
    from .models import Investment
    
    # This would integrate with a real financial API like Alpha Vantage, Yahoo Finance, etc.
    # For now, it's a placeholder
    
    investments = Investment.objects.all()
    updated_count = 0
    
    for investment in investments:
        # Placeholder: In production, fetch real-time prices from API
        # investment.current_price = fetch_price_from_api(investment.symbol)
        # investment.save()
        updated_count += 1
    
    return f"Updated {updated_count} investment prices"


@shared_task
def calculate_monthly_summary(user_id):
    """
    Calculate and cache monthly financial summary for a user
    """
    from django.contrib.auth.models import User
    from django.db.models import Sum
    from .models import Category, Transaction
    from django.core.cache import cache
    
    try:
        user = User.objects.get(id=user_id)
        today = timezone.now().date()
        month_start = today.replace(day=1)
        
        # Calculate income
        income_categories = Category.objects.filter(user=user, type='income')
        total_income = Transaction.objects.filter(
            user=user,
            category__in=income_categories,
            date__range=[month_start, today]
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Calculate expenses
        expense_categories = Category.objects.filter(user=user, type='expense')
        total_expenses = Transaction.objects.filter(
            user=user,
            category__in=expense_categories,
            date__range=[month_start, today]
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        summary = {
            'total_income': float(total_income),
            'total_expenses': float(total_expenses),
            'net_balance': float(total_income - total_expenses),
            'month': month_start.strftime('%Y-%m')
        }
        
        # Cache for 1 hour
        cache_key = f"monthly_summary_{user_id}_{month_start.strftime('%Y-%m')}"
        cache.set(cache_key, summary, 3600)
        
        return f"Calculated monthly summary for user {user_id}"
    except User.DoesNotExist:
        return f"User {user_id} not found"


@shared_task
def send_monthly_report(user_id):
    """
    Send monthly financial report to user
    """
    from django.contrib.auth.models import User
    from .models import UserProfile
    
    try:
        user = User.objects.get(id=user_id)
        user_profile = UserProfile.objects.get(user=user)
        
        if not user_profile.email_notifications:
            return f"Email notifications disabled for user {user_id}"
        
        # Calculate summary
        summary_result = calculate_monthly_summary(user_id)
        
        # Send email with report
        send_mail(
            subject="Your Monthly Financial Report",
            message=f"Hi {user.username},\n\nYour monthly financial report is ready. "
                    f"Log in to view detailed insights.\n\nBest regards,\nFinance Tracker Team",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
        
        return f"Sent monthly report to user {user_id}"
    except User.DoesNotExist:
        return f"User {user_id} not found"


@shared_task
def cleanup_old_data():
    """
    Clean up old data (e.g., old financial records, expired sessions)
    """
    from .models import FinancialRecord
    
    # Delete financial records older than 2 years
    two_years_ago = timezone.now() - timedelta(days=730)
    deleted_count = FinancialRecord.objects.filter(
        created_at__lt=two_years_ago
    ).delete()[0]
    
    return f"Deleted {deleted_count} old financial records"
