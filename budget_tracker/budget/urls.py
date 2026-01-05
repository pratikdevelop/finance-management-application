from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views, views_new_features
from .views import FinancialSummaryView

router = DefaultRouter()
# Existing routes
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'transactions', views.TransactionViewSet, basename='transaction')
router.register(r'budgets', views.BudgetViewSet, basename='budget')

# New feature routes
router.register(r'currencies', views_new_features.CurrencyViewSet, basename='currency')
router.register(r'recurring-transactions', views_new_features.RecurringTransactionViewSet, basename='recurring-transaction')
router.register(r'bill-reminders', views_new_features.BillReminderViewSet, basename='bill-reminder')
router.register(r'shared-accounts', views_new_features.SharedAccountViewSet, basename='shared-account')
router.register(r'financial-goals', views_new_features.FinancialGoalViewSet, basename='financial-goal')
router.register(r'investments', views_new_features.InvestmentViewSet, basename='investment')

urlpatterns = [
    path('', include(router.urls)),
    
    # Existing endpoints
    path('summary/', views.FinancialSummaryView.as_view(), name='financial-summary'),
    path('budget-comparison/', views.BudgetComparisonView.as_view(), name='budget-comparison'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('analyze-expenses/', views.AnalyzeExpensesView.as_view(), name='analyze-expenses'),
    path('predict-expenses/', views.predict_expenses, name='predict-expenses'),
    path('get-records/', views.get_records, name='get-records'),
    path('calculate-salary/', views.CalculateSalaryView.as_view(), name='calculate-salary'),
    
    # JWT Authentication
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # New feature endpoints
    path('ocr/receipt/', views_new_features.OCRReceiptView.as_view(), name='ocr-receipt'),
    path('export/transactions/', views_new_features.ExportTransactionsView.as_view(), name='export-transactions'),
    path('currency/convert/', views_new_features.CurrencyConversionView.as_view(), name='currency-convert'),
    path('2fa/', views_new_features.TwoFactorAuthView.as_view(), name='two-factor-auth'),
]