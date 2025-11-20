from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, Sum
from django.utils import timezone
from datetime import date, datetime
from decimal import Decimal

from .models import Account, JournalEntry, LedgerEntry, AccountBalance
from .serializers import (
    AccountSerializer, JournalEntrySerializer, TransactionCreateSerializer,
    AccountBalanceSerializer
)
from .services import record_transaction, get_account_balance, update_all_balances


class AccountViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and creating accounts
    """
    queryset = Account.objects.filter(is_active=True)
    serializer_class = AccountSerializer
    
    def get_queryset(self):
        """Return all active accounts"""
        return Account.objects.filter(is_active=True)
    
    @action(detail=True, methods=['get'])
    def balance(self, request, pk=None):
        """Get account balance"""
        account = self.get_object()
        as_of_date = request.query_params.get('as_of_date')
        
        if as_of_date:
            try:
                as_of_date = datetime.strptime(as_of_date, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        balance = get_account_balance(account, as_of_date)
        return Response({
            'account': account.account_name,
            'account_number': account.account_number,
            'balance': float(balance),
            'as_of_date': as_of_date or date.today()
        })


class TransactionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for transactions (journal entries)
    """
    queryset = JournalEntry.objects.all()
    serializer_class = JournalEntrySerializer
    
    def get_queryset(self):
        queryset = JournalEntry.objects.all()
        
        # Filter by reference_type
        reference_type = self.request.query_params.get('reference_type')
        if reference_type:
            queryset = queryset.filter(reference_type=reference_type)
        
        # Filter by reference_id
        reference_id = self.request.query_params.get('reference_id')
        if reference_id:
            queryset = queryset.filter(reference_id=reference_id)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(date__gte=date_from)
            except ValueError:
                pass
        if date_to:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(date__lte=date_to)
            except ValueError:
                pass
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """
        Create a new transaction
        Expected format:
        {
            "date": "2024-01-15",
            "description": "Order payment",
            "reference_type": "order",
            "reference_id": "12345",
            "entries": [
                {"account_id": 1, "debit": 100.00, "credit": 0, "description": "Cash received"},
                {"account_id": 4, "debit": 0, "credit": 100.00, "description": "Sales revenue"}
            ]
        }
        """
        serializer = TransactionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        # Convert entries to proper format
        entries = []
        for entry in data['entries']:
            entries.append({
                'account_id': int(entry['account_id']),
                'debit': Decimal(str(entry.get('debit', 0))),
                'credit': Decimal(str(entry.get('credit', 0))),
                'description': entry.get('description', '')
            })
        
        try:
            journal_entry = record_transaction(
                date=data['date'],
                description=data['description'],
                reference_type=data['reference_type'],
                reference_id=data['reference_id'],
                entries=entries
            )
            
            response_serializer = JournalEntrySerializer(journal_entry)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Account.DoesNotExist as e:
            return Response({'error': 'Invalid account ID'}, status=status.HTTP_400_BAD_REQUEST)


class TrialBalanceView(APIView):
    """
    Trial Balance Report
    """
    def get(self, request):
        as_of_date = request.query_params.get('as_of_date')
        if as_of_date:
            try:
                as_of_date = datetime.strptime(as_of_date, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            as_of_date = date.today()
        
        accounts = Account.objects.filter(is_active=True)
        trial_balance = []
        total_debits = Decimal('0.00')
        total_credits = Decimal('0.00')
        
        for account in accounts:
            ledger_entries = LedgerEntry.objects.filter(
                account=account,
                journal_entry__date__lte=as_of_date,
                journal_entry__status='posted'
            )
            
            debit_total = sum(entry.debit for entry in ledger_entries)
            credit_total = sum(entry.credit for entry in ledger_entries)
            
            if account.account_type in ['Asset', 'Expense']:
                balance = debit_total - credit_total
            else:
                balance = credit_total - debit_total
            
            if debit_total > 0 or credit_total > 0:
                trial_balance.append({
                    'account_number': account.account_number,
                    'account_name': account.account_name,
                    'account_type': account.account_type,
                    'debit_total': float(debit_total),
                    'credit_total': float(credit_total),
                    'balance': float(balance)
                })
                
                total_debits += debit_total
                total_credits += credit_total
        
        return Response({
            'as_of_date': as_of_date,
            'accounts': trial_balance,
            'total_debits': float(total_debits),
            'total_credits': float(total_credits),
            'difference': float(total_debits - total_credits)
        })


class ProfitLossView(APIView):
    """
    Simple Profit & Loss Report (Revenue - Expenses)
    """
    def get(self, request):
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if date_from:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            except ValueError:
                date_from = None
        else:
            date_from = date.today().replace(day=1)  # First day of current month
        
        if date_to:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            except ValueError:
                date_to = date.today()
        else:
            date_to = date.today()
        
        # Revenue accounts
        revenue_accounts = Account.objects.filter(account_type='Revenue', is_active=True)
        total_revenue = Decimal('0.00')
        revenue_details = []
        
        for account in revenue_accounts:
            entries = LedgerEntry.objects.filter(
                account=account,
                journal_entry__date__range=[date_from, date_to],
                journal_entry__status='posted'
            )
            revenue = sum(entry.credit - entry.debit for entry in entries)
            if revenue > 0:
                revenue_details.append({
                    'account_name': account.account_name,
                    'amount': float(revenue)
                })
                total_revenue += revenue
        
        # Expense accounts
        expense_accounts = Account.objects.filter(account_type='Expense', is_active=True)
        total_expenses = Decimal('0.00')
        expense_details = []
        
        for account in expense_accounts:
            entries = LedgerEntry.objects.filter(
                account=account,
                journal_entry__date__range=[date_from, date_to],
                journal_entry__status='posted'
            )
            expense = sum(entry.debit - entry.credit for entry in entries)
            if expense > 0:
                expense_details.append({
                    'account_name': account.account_name,
                    'amount': float(expense)
                })
                total_expenses += expense
        
        net_income = total_revenue - total_expenses
        
        return Response({
            'period': {
                'from': date_from,
                'to': date_to
            },
            'revenue': {
                'details': revenue_details,
                'total': float(total_revenue)
            },
            'expenses': {
                'details': expense_details,
                'total': float(total_expenses)
            },
            'net_income': float(net_income)
        })


class BalanceSheetView(APIView):
    """
    Simple Balance Sheet Report (Assets = Liabilities + Equity)
    """
    def get(self, request):
        as_of_date = request.query_params.get('as_of_date')
        if as_of_date:
            try:
                as_of_date = datetime.strptime(as_of_date, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            as_of_date = date.today()
        
        # Assets
        asset_accounts = Account.objects.filter(account_type='Asset', is_active=True)
        total_assets = Decimal('0.00')
        assets = []
        
        for account in asset_accounts:
            balance = get_account_balance(account, as_of_date)
            if balance != 0:
                assets.append({
                    'account_name': account.account_name,
                    'balance': float(balance)
                })
                total_assets += balance if account.account_type == 'Asset' else -balance
        
        # Liabilities
        liability_accounts = Account.objects.filter(account_type='Liability', is_active=True)
        total_liabilities = Decimal('0.00')
        liabilities = []
        
        for account in liability_accounts:
            balance = get_account_balance(account, as_of_date)
            if balance != 0:
                liabilities.append({
                    'account_name': account.account_name,
                    'balance': float(abs(balance))
                })
                total_liabilities += abs(balance)
        
        # Equity
        equity_accounts = Account.objects.filter(account_type='Equity', is_active=True)
        total_equity = Decimal('0.00')
        equity = []
        
        for account in equity_accounts:
            balance = get_account_balance(account, as_of_date)
            if balance != 0:
                equity.append({
                    'account_name': account.account_name,
                    'balance': float(abs(balance))
                })
                total_equity += abs(balance)
        
        return Response({
            'as_of_date': as_of_date,
            'assets': {
                'details': assets,
                'total': float(total_assets)
            },
            'liabilities': {
                'details': liabilities,
                'total': float(total_liabilities)
            },
            'equity': {
                'details': equity,
                'total': float(total_equity)
            },
            'total_liabilities_equity': float(total_liabilities + total_equity),
            'difference': float(total_assets - (total_liabilities + total_equity))
        })
