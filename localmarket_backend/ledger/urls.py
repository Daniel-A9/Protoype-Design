from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AccountViewSet, TransactionViewSet, TrialBalanceView,
    ProfitLossView, BalanceSheetView
)
from .views_web import (
    IndexView, AccountsView, TransactionsView, CreateTransactionView,
    TrialBalanceView as TrialBalanceWebView,
    ProfitLossView as ProfitLossWebView,
    BalanceSheetView as BalanceSheetWebView
)

app_name = 'ledger'

router = DefaultRouter()
router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'transactions', TransactionViewSet, basename='transaction')

urlpatterns = [
    # Web views
    path('', IndexView.as_view(), name='index'),
    path('accounts/', AccountsView.as_view(), name='accounts'),
    path('transactions/', TransactionsView.as_view(), name='transactions'),
    path('transactions/create/', CreateTransactionView.as_view(), name='create_transaction'),
    path('reports/trial-balance/', TrialBalanceWebView.as_view(), name='trial_balance'),
    path('reports/profit-loss/', ProfitLossWebView.as_view(), name='profit_loss'),
    path('reports/balance-sheet/', BalanceSheetWebView.as_view(), name='balance_sheet'),
    
    # API endpoints
    path('api/', include(router.urls)),
    path('api/reports/trial-balance/', TrialBalanceView.as_view(), name='api-trial-balance'),
    path('api/reports/profit-loss/', ProfitLossView.as_view(), name='api-profit-loss'),
    path('api/reports/balance-sheet/', BalanceSheetView.as_view(), name='api-balance-sheet'),
]

