from django.shortcuts import render
from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = 'ledger/index.html'


class AccountsView(TemplateView):
    template_name = 'ledger/accounts/index.html'


class TransactionsView(TemplateView):
    template_name = 'ledger/transactions/index.html'


class CreateTransactionView(TemplateView):
    template_name = 'ledger/create_transaction/index.html'


class TrialBalanceView(TemplateView):
    template_name = 'ledger/trial_balance/index.html'


class ProfitLossView(TemplateView):
    template_name = 'ledger/profit_loss/index.html'


class BalanceSheetView(TemplateView):
    template_name = 'ledger/balance_sheet/index.html'

