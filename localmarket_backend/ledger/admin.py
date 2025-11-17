from django.contrib import admin
from .models import Account, JournalEntry, LedgerEntry, AccountBalance


class LedgerEntryInline(admin.TabularInline):
    model = LedgerEntry
    extra = 2
    fields = ('account', 'debit', 'credit', 'description')
    readonly_fields = ()


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['account_number', 'account_name', 'account_type', 'normal_balance', 'is_active', 'get_balance']
    list_filter = ['account_type', 'is_active', 'normal_balance']
    search_fields = ['account_number', 'account_name']
    ordering = ['account_number']
    
    def get_balance(self, obj):
        try:
            balance = obj.balance.net_balance
            return f"${balance:,.2f}"
        except AccountBalance.DoesNotExist:
            return "$0.00"
    get_balance.short_description = 'Balance'


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ['entry_number', 'date', 'description', 'reference_type', 'reference_id', 'status', 'get_total_debits', 'get_total_credits']
    list_filter = ['status', 'reference_type', 'date']
    search_fields = ['description', 'reference_id', 'entry_number']
    readonly_fields = ['entry_number', 'created_at', 'updated_at']
    inlines = [LedgerEntryInline]
    date_hierarchy = 'date'
    
    fieldsets = (
        (None, {
            'fields': ('entry_number', 'date', 'description', 'status')
        }),
        ('Reference Information', {
            'fields': ('reference_type', 'reference_id'),
            'description': 'Link to external systems (orders, payments, etc.)'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_total_debits(self, obj):
        return f"${obj.total_debits:,.2f}"
    get_total_debits.short_description = 'Total Debits'
    
    def get_total_credits(self, obj):
        return f"${obj.total_credits:,.2f}"
    get_total_credits.short_description = 'Total Credits'
    
    def save_model(self, request, obj, form, change):
        # Auto-post entry if status is posted
        super().save_model(request, obj, form, change)
        if obj.status == 'posted' and not change:
            # Update balances when posting
            from .services import update_all_balances
            update_all_balances()
    
    def save_formset(self, request, form, formset, change):
        # Validate debits = credits when saving inline entries
        instances = formset.save(commit=False)
        total_debits = sum(entry.debit for entry in instances if hasattr(entry, 'debit'))
        total_credits = sum(entry.credit for entry in instances if hasattr(entry, 'credit'))
        
        if abs(total_debits - total_credits) > 0.01:
            from django.core.exceptions import ValidationError
            raise ValidationError(f"Debits ({total_debits}) must equal credits ({total_credits})")
        
        for instance in instances:
            instance.save()
        formset.save_m2m()


@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    list_display = ['id', 'journal_entry', 'account', 'debit', 'credit', 'description']
    list_filter = ['account', 'journal_entry__date']
    search_fields = ['description', 'account__account_name', 'journal_entry__entry_number']
    readonly_fields = []


@admin.register(AccountBalance)
class AccountBalanceAdmin(admin.ModelAdmin):
    list_display = ['account', 'balance_as_of_date', 'debit_total', 'credit_total', 'net_balance', 'last_updated']
    list_filter = ['balance_as_of_date', 'account__account_type']
    search_fields = ['account__account_name', 'account__account_number']
    readonly_fields = ['last_updated']
    
    def has_add_permission(self, request):
        return False  # Balances are auto-generated
