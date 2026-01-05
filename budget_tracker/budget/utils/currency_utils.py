"""
Utility functions for currency conversion
"""
from forex_python.converter import CurrencyRates
from decimal import Decimal
from django.core.cache import cache


def get_exchange_rate(from_currency, to_currency):
    """
    Get exchange rate between two currencies with caching
    """
    cache_key = f"exchange_rate_{from_currency}_{to_currency}"
    
    # Check cache first (cache for 1 hour)
    cached_rate = cache.get(cache_key)
    if cached_rate:
        return Decimal(str(cached_rate))
    
    try:
        c = CurrencyRates()
        rate = c.get_rate(from_currency, to_currency)
        
        # Cache the rate for 1 hour (3600 seconds)
        cache.set(cache_key, rate, 3600)
        
        return Decimal(str(rate))
    except Exception as e:
        print(f"Error getting exchange rate: {e}")
        # Return 1 as fallback (no conversion)
        return Decimal('1')


def convert_amount(amount, from_currency, to_currency):
    """
    Convert amount from one currency to another
    """
    if from_currency == to_currency:
        return amount
    
    rate = get_exchange_rate(from_currency, to_currency)
    converted_amount = Decimal(str(amount)) * rate
    
    return converted_amount.quantize(Decimal('0.01'))


def get_all_exchange_rates(base_currency='USD'):
    """
    Get all exchange rates for a base currency
    """
    cache_key = f"all_rates_{base_currency}"
    
    # Check cache first
    cached_rates = cache.get(cache_key)
    if cached_rates:
        return cached_rates
    
    try:
        c = CurrencyRates()
        rates = c.get_rates(base_currency)
        
        # Cache for 1 hour
        cache.set(cache_key, rates, 3600)
        
        return rates
    except Exception as e:
        print(f"Error getting all exchange rates: {e}")
        return {}


def format_currency(amount, currency_code):
    """
    Format amount with currency symbol
    """
    from ..models import Currency
    
    try:
        currency = Currency.objects.get(code=currency_code)
        return f"{currency.symbol}{amount:.2f}"
    except Currency.DoesNotExist:
        return f"{amount:.2f} {currency_code}"
