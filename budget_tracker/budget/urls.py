from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'transactions', views.TransactionViewSet, basename='transaction')
router.register(r'budgets', views.BudgetViewSet, basename='budget')

urlpatterns = [
    path('', include(router.urls)),
    path('summary/', views.FinancialSummaryView.as_view(), name='financial-summary'),
    path('budget-comparison/', views.BudgetComparisonView.as_view(), name='budget-comparison'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('predict-expenses/', views.predict_expenses, name='predict-expenses'),
    path('get-records/', views.get_records, name='get-records'),
]