from django.shortcuts import render
from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = 'ledger/index.html'


class AccountsView(TemplateView):
    template_name = 'ledger/accounts.html'


class TransactionsView(TemplateView):
    template_name = 'ledger/transactions.html'


class CreateTransactionView(TemplateView):
    template_name = 'ledger/create_transaction.html'


class TrialBalanceView(TemplateView):
    template_name = 'ledger/trial_balance.html'


class ProfitLossView(TemplateView):
    template_name = 'ledger/profit_loss.html'


class BalanceSheetView(TemplateView):
    template_name = 'ledger/balance_sheet.html'

