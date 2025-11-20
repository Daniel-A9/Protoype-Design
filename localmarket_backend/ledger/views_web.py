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


class CreateTransactionEntryView(TemplateView):
    template_name = 'ledger/create_transaction/entry/index.html'


class TrialBalanceView(TemplateView):
    template_name = 'ledger/trial_balance/index.html'


class ProfitLossView(TemplateView):
    template_name = 'ledger/profit_loss/index.html'


class BalanceSheetView(TemplateView):
    template_name = 'ledger/balance_sheet/index.html'


class InventoryView(TemplateView):
    template_name = 'ledger/inventory/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Placeholder product data - replace with actual product model queries when available
        context['products'] = [
            {
                'id': 'citrus-ipa',
                'name': 'Citrus IPA',
                'image': 'https://images.unsplash.com/photo-1608270586620-248524c67de9?w=300&h=200&fit=crop',
            },
            {
                'id': 'chocolate-stout',
                'name': 'Chocolate Stout',
                'image': 'https://images.unsplash.com/photo-1571613316887-6f8d5cbf7ef7?w=300&h=200&fit=crop',
            },
            {
                'id': 'golden-lager',
                'name': 'Golden Lager',
                'image': 'https://images.unsplash.com/photo-1581636625402-29b2a704ef13?w=300&h=200&fit=crop',
            },
            {
                'id': 'hefeweizen',
                'name': 'Hefeweizen',
                'image': 'https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=300&h=200&fit=crop',
            },
            {
                'id': 'pale-ale',
                'name': 'Pale Ale',
                'image': 'https://images.unsplash.com/photo-1608270586620-248524c67de9?w=300&h=200&fit=crop',
            },
        ]
        return context
