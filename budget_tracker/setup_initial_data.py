"""
Script to set up initial data for the finance management application
Run this after migrations: python manage.py shell < setup_initial_data.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'budget_tracker.settings')
django.setup()

from budget.models import Currency

def setup_currencies():
    """Create initial currency data"""
    currencies = [
        {'code': 'USD', 'name': 'US Dollar', 'symbol': '$'},
        {'code': 'EUR', 'name': 'Euro', 'symbol': '€'},
        {'code': 'GBP', 'name': 'British Pound', 'symbol': '£'},
        {'code': 'JPY', 'name': 'Japanese Yen', 'symbol': '¥'},
        {'code': 'INR', 'name': 'Indian Rupee', 'symbol': '₹'},
        {'code': 'CAD', 'name': 'Canadian Dollar', 'symbol': 'C$'},
        {'code': 'AUD', 'name': 'Australian Dollar', 'symbol': 'A$'},
        {'code': 'CHF', 'name': 'Swiss Franc', 'symbol': 'CHF'},
        {'code': 'CNY', 'name': 'Chinese Yuan', 'symbol': '¥'},
        {'code': 'SEK', 'name': 'Swedish Krona', 'symbol': 'kr'},
    ]
    
    created_count = 0
    for curr_data in currencies:
        currency, created = Currency.objects.get_or_create(
            code=curr_data['code'],
            defaults={
                'name': curr_data['name'],
                'symbol': curr_data['symbol']
            }
        )
        if created:
            created_count += 1
            print(f"Created currency: {currency.code} - {currency.name}")
        else:
            print(f"Currency already exists: {currency.code}")
    
    print(f"\nTotal currencies created: {created_count}")
    print(f"Total currencies in database: {Currency.objects.count()}")

if __name__ == '__main__':
    print("Setting up initial data...\n")
    setup_currencies()
    print("\nSetup complete!")
