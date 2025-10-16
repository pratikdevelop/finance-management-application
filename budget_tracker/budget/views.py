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
from .models import Category, Transaction, Budget, UserProfile
from .serializers import (
    CategorySerializer, TransactionSerializer, BudgetSerializer,
    FinancialSummarySerializer, UserSerializer, UserProfileSerializer
)

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
        
        # Filter by category if provided
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
            
        # Filter by period (month/year) if provided
        month = self.request.query_params.get('month')
        if month:
            queryset = queryset.filter(month=month)
            
        year = self.request.query_params.get('year')
        if year:
            queryset = queryset.filter(year=year)
            
        return queryset

class FinancialSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Get date range parameters or default to current month
        today = timezone.now().date()
        
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        if start_date_str and end_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {"error": "Invalid date format. Use YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            start_date = today.replace(day=1)
            end_date = today
        
        # Calculate income
        income_categories = Category.objects.filter(user=request.user, type='income')
        total_income = Transaction.objects.filter(
            user=request.user,
            category__in=income_categories,
            date__range=[start_date, end_date]
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Calculate expenses
        expense_categories = Category.objects.filter(user=request.user, type='expense')
        total_expenses = Transaction.objects.filter(
            user=request.user,
            category__in=expense_categories,
            date__range=[start_date, end_date]
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Calculate balance
        balance = total_income - total_expenses
        
        # Calculate expenses by category
        expenses_by_category = []
        for category in expense_categories:
            category_expenses = Transaction.objects.filter(
                user=request.user,
                category=category,
                date__range=[start_date, end_date]
            ).aggregate(total=Sum('amount'))['total'] or 0
            if category_expenses > 0:
                expenses_by_category.append({
                    'category': category.name,
                    'amount': category_expenses
                })

        # Calculate monthly trend for the last 6 months
        monthly_trend = []
        for i in range(6):
            month_start = (today - relativedelta(months=i)).replace(day=1)
            month_end = month_start + relativedelta(months=1) - relativedelta(days=1)

            monthly_income = Transaction.objects.filter(
                user=request.user,
                category__in=income_categories,
                date__range=[month_start, month_end]
            ).aggregate(total=Sum('amount'))['total'] or 0

            monthly_expenses = Transaction.objects.filter(
                user=request.user,
                category__in=expense_categories,
                date__range=[month_start, month_end]
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            monthly_trend.append({
                'month': month_start.strftime('%Y-%m'),
                'income': monthly_income,
                'expenses': monthly_expenses
            })
        monthly_trend.reverse() # Show in chronological order

        summary = {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_balance': balance,
            'expenses_by_category': expenses_by_category,
            'monthly_trend': monthly_trend
        }
        
        serializer = FinancialSummarySerializer(summary)
        return Response(serializer.data)

class BudgetComparisonView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Get month parameter or default to current month
        month_param = request.query_params.get('month')
        if month_param:
            try:
                month_date = datetime.strptime(month_param, '%Y-%m').date()
            except ValueError:
                return Response(
                    {"error": "Invalid month format. Use YYYY-MM"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            today = timezone.now().date()
            month_date = today.replace(day=1)
        
        # Get next month for date range
        next_month = month_date + relativedelta(months=1)
        
        # Get all expense categories
        expense_categories = Category.objects.filter(user=request.user, type='expense')
        
        # Initialize result
        result = []
        
        for category in expense_categories:
            # Get budget for this category and month
            print(f"Filtering budget for user: {request.user.id}, category: {category.id}, month: {month_date.strftime('%m')}, year: {month_date.year}")
            budget = Budget.objects.filter(
                user=request.user,
                category=category,
                month=month_date.strftime('%m'),  # Use two-digit string month to match CharField
                year=month_date.year
            ).first()
            
            # Get actual expenses for this category and month
            actual_expenses = Transaction.objects.filter(
                user=request.user,
                category=category,
                date__gte=month_date,
                date__lt=next_month
            ).aggregate(total=Sum('amount'))['total'] or 0
            print(f"Calculated actual expenses for category {category.name}: {actual_expenses}")
            
            # Add to result
            result.append({
                'category_id': category.id,
                'category_name': category.name,
                'budget_amount': budget.amount if budget else 0,
                'actual_amount': actual_expenses,
                'difference': (budget.amount if budget else 0) - actual_expenses,
                'year': month_date.year,
                'month': int(month_date.strftime('%m'))
            })
        
        return Response(result)

class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data)

    def put(self, request):
        user_profile = request.user.userprofile
        serializer = UserProfileSerializer(user_profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # Update User model fields if present in request data
            user = request.user
            if 'username' in request.data:
                user.username = request.data['username']
            if 'email' in request.data:
                user.email = request.data['email']
            user.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def signup(request):
    try:
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not username or not email or not password:
            return Response(
                {'error': 'Username, email, and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if User.objects.filter(username=username).exists():
            return Response(
                {'error': 'Username already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'Email already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        UserProfile.objects.create(user=user)

        authenticated_user = authenticate(request, username=username, password=password)

        if authenticated_user is not None:
            token, created = Token.objects.get_or_create(user=authenticated_user)
            return Response(
                {'message': 'User created successfully', 'token': token.key, 'username': authenticated_user.username},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'error': 'Authentication failed after user creation'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')
    print(email, password)


    if not email or not password:
        return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, username=user.username, password=password)

    if user is not None:
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'username': user.username})
    else:
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def predict_expenses(request):
    return Response({"message": "Predict expenses endpoint (placeholder)"}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_records(request):
    return Response({"message": "Get records endpoint (placeholder)"}, status=status.HTTP_200_OK)
