"""
Views for new features: recurring transactions, bill reminders, shared accounts, 
financial goals, investments, OCR, export, and currency conversion
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from django.db.models import Q
from django.utils import timezone
from datetime import datetime
import pyotp
import qrcode
from io import BytesIO
import base64
from dateutil.relativedelta import relativedelta

from .models import (
    RecurringTransaction, BillReminder, SharedAccount, SharedAccountMember,
    FinancialGoal, Investment, Currency, Transaction, UserProfile
)
from .serializers import (
    RecurringTransactionSerializer, BillReminderSerializer,
    SharedAccountSerializer, SharedAccountMemberSerializer,
    FinancialGoalSerializer, InvestmentSerializer, CurrencySerializer,
    TransactionSerializer
)
from .utils.ocr_utils import process_receipt_image
from .utils.export_utils import (
    export_transactions_to_csv, export_transactions_to_excel,
    export_transactions_to_pdf, export_financial_summary_to_pdf
)
from .utils.currency_utils import convert_amount, get_exchange_rate


class CurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for listing and retrieving currencies
    """
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    permission_classes = [permissions.IsAuthenticated]


class RecurringTransactionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing recurring transactions
    """
    serializer_class = RecurringTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = RecurringTransaction.objects.filter(user=self.request.user)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter by frequency
        frequency = self.request.query_params.get('frequency')
        if frequency:
            queryset = queryset.filter(frequency=frequency)
        
        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        # Calculate next_occurrence based on start_date and frequency
        start_date = serializer.validated_data.get('start_date')
        frequency = serializer.validated_data.get('frequency')

        if start_date and frequency:
            next_occurrence = start_date
            if frequency == 'daily':
                next_occurrence += relativedelta(days=1)
            elif frequency == 'weekly':
                next_occurrence += relativedelta(weeks=1)
            elif frequency == 'monthly':
                next_occurrence += relativedelta(months=1)
            elif frequency == 'annually':
                next_occurrence += relativedelta(years=1)
            serializer.validated_data['next_occurrence'] = next_occurrence
        
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle active status of recurring transaction"""
        recurring_trans = self.get_object()
        recurring_trans.is_active = not recurring_trans.is_active
        recurring_trans.save()
        serializer = self.get_serializer(recurring_trans)
        return Response(serializer.data)


    @action(detail=False, methods=['get'])
    def summary_statistics(self, request):
        """Get summary statistics for recurring transactions"""
        user = request.user
        today = timezone.now().date()

        # Total Active
        total_active = RecurringTransaction.objects.filter(user=user, is_active=True).count()

        # Monthly Total (for current month)
        current_month_start = today.replace(day=1)
        current_month_end = current_month_start + relativedelta(months=1) - relativedelta(days=1)
        monthly_total = RecurringTransaction.objects.filter(
            user=user,
            is_active=True,
            next_occurrence__gte=current_month_start,
            next_occurrence__lte=current_month_end
        ).aggregate(total=Sum('amount'))['total'] or 0

        # Next 7 Days
        next_7_days_end = today + relativedelta(days=7)
        next_7_days = RecurringTransaction.objects.filter(
            user=user,
            is_active=True,
            next_occurrence__gte=today,
            next_occurrence__lte=next_7_days_end
        ).count()

        # All Transactions
        all_transactions = RecurringTransaction.objects.filter(user=user).count()

        summary = {
            'total_active': total_active,
            'monthly_total': monthly_total,
            'next_7_days': next_7_days,
            'all_transactions': all_transactions,
        }
        serializer = RecurringTransactionSummarySerializer(summary)
        return Response(serializer.data)

class BillReminderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing bill reminders
    """
    serializer_class = BillReminderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = BillReminder.objects.filter(user=self.request.user)
        
        # Filter by paid status
        is_paid = self.request.query_params.get('is_paid')
        if is_paid is not None:
            queryset = queryset.filter(is_paid=is_paid.lower() == 'true')
        
        # Filter by upcoming (due in next N days)
        upcoming_days = self.request.query_params.get('upcoming_days')
        if upcoming_days:
            try:
                days = int(upcoming_days)
                end_date = timezone.now().date() + timezone.timedelta(days=days)
                queryset = queryset.filter(
                    is_paid=False,
                    due_date__lte=end_date,
                    due_date__gte=timezone.now().date()
                )
            except ValueError:
                pass
        
        return queryset.order_by('due_date')
    
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark bill as paid"""
        bill = self.get_object()
        bill.is_paid = True
        bill.paid_date = timezone.now().date()
        bill.save()
        serializer = self.get_serializer(bill)
        return Response(serializer.data)


class SharedAccountViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing shared accounts
    """
    serializer_class = SharedAccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Return accounts owned by or shared with the user
        return SharedAccount.objects.filter(
            Q(owner=self.request.user) | Q(members=self.request.user)
        ).distinct()
    
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """Add a member to shared account"""
        shared_account = self.get_object()
        
        # Check if user is owner or admin
        if shared_account.owner != request.user:
            member = SharedAccountMember.objects.filter(
                shared_account=shared_account,
                user=request.user
            ).first()
            if not member or member.role not in ['owner', 'admin']:
                return Response(
                    {'error': 'Only owners and admins can add members'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Add member
        user_id = request.data.get('user_id')
        role = request.data.get('role', 'member')
        
        try:
            from django.contrib.auth.models import User
            user = User.objects.get(id=user_id)
            
            member, created = SharedAccountMember.objects.get_or_create(
                shared_account=shared_account,
                user=user,
                defaults={'role': role}
            )
            
            if not created:
                return Response(
                    {'error': 'User is already a member'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = SharedAccountMemberSerializer(member)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def remove_member(self, request, pk=None):
        """Remove a member from shared account"""
        shared_account = self.get_object()
        
        # Check permissions
        if shared_account.owner != request.user:
            return Response(
                {'error': 'Only owner can remove members'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user_id = request.data.get('user_id')
        try:
            SharedAccountMember.objects.filter(
                shared_account=shared_account,
                user_id=user_id
            ).delete()
            return Response({'message': 'Member removed successfully'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class FinancialGoalViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing financial goals
    """
    serializer_class = FinancialGoalSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = FinancialGoal.objects.filter(user=self.request.user)
        
        # Filter by completion status
        is_completed = self.request.query_params.get('is_completed')
        if is_completed is not None:
            queryset = queryset.filter(is_completed=is_completed.lower() == 'true')
        
        # Filter by goal type
        goal_type = self.request.query_params.get('goal_type')
        if goal_type:
            queryset = queryset.filter(goal_type=goal_type)
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        """Update progress on a financial goal"""
        goal = self.get_object()
        amount = request.data.get('amount')
        
        if not amount:
            return Response(
                {'error': 'Amount is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from decimal import Decimal
            amount = Decimal(str(amount))
            goal.current_amount += amount
            
            # Check if goal is completed
            if goal.current_amount >= goal.target_amount:
                goal.is_completed = True
                goal.completed_date = timezone.now().date()
            
            goal.save()
            serializer = self.get_serializer(goal)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class InvestmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing investment portfolio
    """
    serializer_class = InvestmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Investment.objects.filter(user=self.request.user)
        
        # Filter by investment type
        investment_type = self.request.query_params.get('investment_type')
        if investment_type:
            queryset = queryset.filter(investment_type=investment_type)
        
        return queryset.order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def portfolio_summary(self, request):
        """Get portfolio summary with total value and profit/loss"""
        investments = self.get_queryset()
        
        total_value = sum(inv.total_value for inv in investments)
        total_cost = sum(inv.total_cost for inv in investments)
        total_profit_loss = total_value - total_cost
        total_profit_loss_percentage = (
            (total_profit_loss / total_cost * 100) if total_cost > 0 else 0
        )
        
        summary = {
            'total_investments': investments.count(),
            'total_value': float(total_value),
            'total_cost': float(total_cost),
            'total_profit_loss': float(total_profit_loss),
            'total_profit_loss_percentage': float(total_profit_loss_percentage),
            'by_type': {}
        }
        
        # Group by investment type
        for inv_type in Investment.INVESTMENT_TYPE_CHOICES:
            type_investments = investments.filter(investment_type=inv_type[0])
            if type_investments.exists():
                type_value = sum(inv.total_value for inv in type_investments)
                summary['by_type'][inv_type[0]] = {
                    'count': type_investments.count(),
                    'total_value': float(type_value)
                }
        
        return Response(summary)


class OCRReceiptView(APIView):
    """
    View for processing receipt images with OCR
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Process uploaded receipt image"""
        if 'receipt_image' not in request.FILES:
            return Response(
                {'error': 'No receipt image provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        receipt_image = request.FILES['receipt_image']
        
        # Save temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            for chunk in receipt_image.chunks():
                tmp_file.write(chunk)
            tmp_path = tmp_file.name
        
        try:
            # Process with OCR
            result = process_receipt_image(tmp_path)
            
            # Clean up temp file
            import os
            os.unlink(tmp_path)
            
            return Response(result)
        except Exception as e:
            return Response(
                {'error': f'Error processing receipt: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ExportTransactionsView(APIView):
    """
    View for exporting transactions to various formats
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Export transactions based on format parameter"""
        export_format = request.query_params.get('format', 'csv').lower()
        
        # Get transactions with filters
        transactions = Transaction.objects.filter(user=request.user)
        
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            transactions = transactions.filter(date__gte=start_date)
        if end_date:
            transactions = transactions.filter(date__lte=end_date)
        
        transactions = transactions.select_related('category', 'currency', 'shared_account').order_by('-date')
        
        try:
            if export_format == 'csv':
                data = export_transactions_to_csv(transactions)
                response = HttpResponse(data, content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="transactions.csv"'
                return response
            
            elif export_format == 'excel':
                data = export_transactions_to_excel(transactions)
                response = HttpResponse(
                    data,
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = 'attachment; filename="transactions.xlsx"'
                return response
            
            elif export_format == 'pdf':
                data = export_transactions_to_pdf(transactions, request.user)
                response = HttpResponse(data, content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="transactions.pdf"'
                return response
            
            else:
                return Response(
                    {'error': 'Invalid format. Use csv, excel, or pdf'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {'error': f'Error exporting: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CurrencyConversionView(APIView):
    """
    View for currency conversion
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Convert amount between currencies"""
        amount = request.data.get('amount')
        from_currency = request.data.get('from_currency')
        to_currency = request.data.get('to_currency')
        
        if not all([amount, from_currency, to_currency]):
            return Response(
                {'error': 'amount, from_currency, and to_currency are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from decimal import Decimal
            amount = Decimal(str(amount))
            converted_amount = convert_amount(amount, from_currency, to_currency)
            exchange_rate = get_exchange_rate(from_currency, to_currency)
            
            return Response({
                'original_amount': float(amount),
                'from_currency': from_currency,
                'to_currency': to_currency,
                'converted_amount': float(converted_amount),
                'exchange_rate': float(exchange_rate)
            })
        except Exception as e:
            return Response(
                {'error': f'Conversion error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TwoFactorAuthView(APIView):
    """
    View for Two-Factor Authentication setup and verification
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get 2FA setup information (QR code)"""
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        if not user_profile.two_factor_secret:
            # Generate new secret
            user_profile.two_factor_secret = pyotp.random_base32()
            user_profile.save()
        
        # Generate provisioning URI
        totp = pyotp.TOTP(user_profile.two_factor_secret)
        provisioning_uri = totp.provisioning_uri(
            name=request.user.email,
            issuer_name='Finance Tracker'
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return Response({
            'secret': user_profile.two_factor_secret,
            'qr_code': f'data:image/png;base64,{qr_code_base64}',
            'enabled': user_profile.two_factor_enabled
        })
    
    def post(self, request):
        """Verify 2FA token and enable 2FA"""
        token = request.data.get('token')
        
        if not token:
            return Response(
                {'error': 'Token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_profile = UserProfile.objects.get(user=request.user)
        totp = pyotp.TOTP(user_profile.two_factor_secret)
        
        if totp.verify(token):
            user_profile.two_factor_enabled = True
            user_profile.save()
            return Response({'message': '2FA enabled successfully'})
        else:
            return Response(
                {'error': 'Invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def delete(self, request):
        """Disable 2FA"""
        user_profile = UserProfile.objects.get(user=request.user)
        user_profile.two_factor_enabled = False
        user_profile.save()
        return Response({'message': '2FA disabled successfully'})
