from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import Category, Transaction, Budget, UserProfile, FinancialRecord
from .serializers import (
    CategorySerializer, TransactionSerializer, BudgetSerializer,
    FinancialSummarySerializer, UserSerializer, UserProfileSerializer
)

TAX_BRACKETS = [
    {'limit': 1000, 'rate': 0.10},
    {'limit': 4000, 'rate': 0.15},
    {'limit': float('inf'), 'rate': 0.25}
]


def calculate_tax(gross_pay):
    tax = 0
    remaining = gross_pay
    for bracket in TAX_BRACKETS:
        if remaining <= 0:
            break
        taxable = min(remaining, bracket['limit'])
        tax += taxable * bracket['rate']
        remaining -= taxable
    return tax

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Category.objects.filter(user=self.request.user)
        
        # Filter by name if provided
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__icontains=name)
            
        # Filter by type if provided
        category_type = self.request.query_params.get('type')
        if category_type:
            queryset = queryset.filter(type=category_type)
            
        return queryset

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Transaction.objects.filter(user=self.request.user)
        
        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
            
        # Filter by category if provided
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
            
        # Filter by amount range if provided
        min_amount = self.request.query_params.get('min_amount')
        max_amount = self.request.query_params.get('max_amount')
        if min_amount:
            queryset = queryset.filter(amount__gte=min_amount)
        if max_amount:
            queryset = queryset.filter(amount__lte=max_amount)
            
        # Filter by transaction type if provided
        transaction_type = self.request.query_params.get('transaction_type')
        if transaction_type:
            queryset = queryset.filter(category__type=transaction_type)
            
        return queryset.order_by('-date')

class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Budget.objects.filter(user=self.request.user)
        
    def post(self, request):
        try:
            data = request.data
            if not data or 'rates' not in data:
                return Response({'error': 'Missing rates data'}, status=status.HTTP_400_BAD_REQUEST)

            total_regular_hours = 0
            total_overtime_hours = 0
            gross_pay = 0

            for entry in data['rates']:
                rate = float(entry['rate'])
                hours = float(entry['hours'])
                if hours <= 40:
                    regular_pay = hours * rate
                    overtime_pay = 0
                else:
                    regular_pay = 40 * rate
                    overtime_hours = hours - 40
                    overtime_pay = overtime_hours * (rate * 1.5)
                total_regular_hours += min(hours, 40)
                total_overtime_hours += max(0, hours - 40)
                gross_pay += regular_pay + overtime_pay

            tax_amount = calculate_tax(gross_pay)
            net_pay = gross_pay - tax_amount

            monthly_gross = gross_pay * 4.33
            monthly_net = net_pay * 4.33
            yearly_gross = gross_pay * 52
            yearly_net = net_pay * 52

            result = {
                'weekly': {
                    'regular_hours': round(total_regular_hours, 1),
                    'overtime_hours': round(total_overtime_hours, 1),
                    'gross_pay': round(gross_pay, 2),
                    'tax_amount': round(tax_amount, 2),
                    'net_pay': round(net_pay, 2)
                },
                'monthly': {
                    'gross': round(monthly_gross, 2),
                    'net': round(monthly_net, 2)
                },
                'yearly': {
                    'gross': round(yearly_gross, 2),
                    'net': round(yearly_net, 2)
                },
                'created_at': timezone.now().isoformat()
            }

            # Save data to FinancialRecord model
            FinancialRecord.objects.create(
                user=request.user,
                data={
                    "weekly_gross_pay": round(gross_pay, 2),
                    "weekly_net_pay": round(net_pay, 2),
                    "monthly_gross_pay": round(monthly_gross, 2),
                    "monthly_net_pay": round(monthly_net, 2),
                    "yearly_gross_pay": round(yearly_gross, 2),
                    "yearly_net_pay": round(yearly_net, 2),
                },
                record_type="salary_calculation",
            )

            # Placeholder for SocketIO emission
            # socketio.emit('new_record', {'message': 'New financial record added'}, room=request.user.id)

            return Response(result, status=status.HTTP_200_OK)
        except (ValueError, KeyError) as e:
            return Response({'error': f'Invalid input data: {e}'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Placeholder AI functions
def categorize_expense_ai(description):
    """Placeholder for AI expense categorization."""
    return "Uncategorized"

def train_expense_model_ai(user_id, expenses):
    """Placeholder for AI expense model training."""
    pass

def generate_recommendations_ai(user_id, analysis_results):
    """Placeholder for AI recommendation generation."""
    return ["No recommendations yet."]


class FinancialSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        # Default to current month if no month/year provided
        month = int(request.query_params.get('month', timezone.now().month))
        year = int(request.query_params.get('year', timezone.now().year))

        summary_data = calculate_financial_summary(user, month, year)
        serializer = FinancialSummarySerializer(summary_data)
        return Response(serializer.data)

def calculate_financial_summary(user, month, year):
    # Placeholder for financial summary calculation logic
    # This function would typically query Transaction and Budget models
    # to aggregate data for the given user, month, and year.
    # For now, it returns dummy data.
    return {
        'total_income': 1000.00,
        'total_expenses': 500.00,
        'net_savings': 500.00,
        'income_by_category': {'Salary': 1000.00},
        'expenses_by_category': {'Rent': 300.00, 'Food': 200.00},
        'balance_history': [
            {'date': '2023-01-01', 'balance': 1000.00},
            {'date': '2023-01-15', 'balance': 700.00},
            {'date': '2023-01-31', 'balance': 500.00},
        ]
    }


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user_profile = getattr(request.user, 'userprofile', None)
        if user_profile is None:
            return Response({"detail": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserProfileSerializer(user_profile, context={'request': request})
        return Response(serializer.data)

    def put(self, request):
        user_profile = getattr(request.user, 'userprofile', None)
        if user_profile is None:
            return Response({"detail": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserProfileSerializer(user_profile, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BudgetComparisonView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Placeholder for budget comparison logic
        # This would typically involve comparing actual spending against budget allocations
        # For now, return dummy data
        return Response({
            'message': 'Budget comparison data will be here',
            'comparison_data': []
        })


class CalculateSalaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Placeholder for salary calculation logic
        # This would typically take input like hourly rate, hours worked, etc.
        # For now, return dummy data
        return Response({
            'message': 'Salary calculation will be here',
            'net_pay': 0.00
        })


class AnalyzeExpensesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')

        if not all([start_date_str, end_date_str]):
            return Response({"error": "Start date and end date are required."}, status=status.HTTP_400_BAD_REQUEST)

        start_date = datetime.fromisoformat(start_date_str)
        end_date = datetime.fromisoformat(end_date_str)

        transactions = Transaction.objects.filter(
            user=user,
            date__range=[start_date, end_date]
        ).order_by('-date')

        if not transactions.exists():
            return Response({"message": "No transactions found for the specified period."}, status=status.HTTP_200_OK)

        # Categorize expenses (using placeholder AI function)
        categorized_expenses = []
        for transaction in transactions:
            category = categorize_expense_ai(transaction.description)
            categorized_expenses.append({
                "description": transaction.description,
                "amount": float(transaction.amount),
                "category": category,
                "date": transaction.date.isoformat()
            })

        # Train expense model (using placeholder AI function)
        train_expense_model_ai(user.id, categorized_expenses)

        # Perform basic analysis (can be expanded with more sophisticated logic)
        total_expenses = sum(item['amount'] for item in categorized_expenses)
        expenses_by_category = {}
        for item in categorized_expenses:
            expenses_by_category[item['category']] = expenses_by_category.get(item['category'], 0) + item['amount']

        # Generate recommendations (using placeholder AI function)
        recommendations = generate_recommendations_ai(user.id, {"total_expenses": total_expenses, "expenses_by_category": expenses_by_category})

        analysis_results = {
            "total_expenses": round(total_expenses, 2),
            "expenses_by_category": {k: round(v, 2) for k, v in expenses_by_category.items()},
            "recommendations": recommendations,
            "categorized_expenses": categorized_expenses,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "generated_at": timezone.now().isoformat()
        }

        # Save analysis results to FinancialRecord model
        FinancialRecord.objects.create(
            user=user,
            data=analysis_results,
            record_type="expense_analysis"
        )

        # Placeholder for SocketIO emission
        # socketio.emit('expense_analysis_completed', analysis_results, room=str(user.id))

        return Response(analysis_results, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def predict_expenses(request):
    return Response({"message": "Predict expenses endpoint (placeholder)"}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_records(request):
    return Response({"message": "Get records endpoint (placeholder)"}, status=status.HTTP_200_OK)



class SignupView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        email = request.data.get('email')
        username = request.data.get('username')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        password = request.data.get('password')

        if not all([email, username, first_name, last_name, password]):
            return Response({'message': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'message': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'username': user.username}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'message': f'Registration failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'username': user.username})
        else:
            return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)