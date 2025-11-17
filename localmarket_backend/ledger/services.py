"""
Ledger business logic services
"""
from decimal import Decimal
from datetime import date
from django.db import transaction
from django.utils import timezone
from .models import Account, JournalEntry, LedgerEntry, AccountBalance


def record_transaction(date, description, reference_type, reference_id, entries):
    """
    Main function to record any transaction.
    
    Args:
        date: Transaction date
        description: Transaction description
        reference_type: External system identifier (e.g., "order", "payment", "subscription")
        reference_id: External system's ID (string)
        entries: List of dicts with {account_id, debit, credit, description}
    
    Returns:
        JournalEntry instance
    
    Raises:
        ValueError: If debits don't equal credits or validation fails
    """
    # Validate entries
    total_debits = sum(Decimal(str(e.get('debit', 0))) for e in entries)
    total_credits = sum(Decimal(str(e.get('credit', 0))) for e in entries)
    
    if total_debits != total_credits:
        raise ValueError(f"Debits ({total_debits}) must equal credits ({total_credits})")
    
    if not entries or len(entries) < 2:
        raise ValueError("A transaction must have at least two entries")
    
    with transaction.atomic():
        # Create journal entry
        journal_entry = JournalEntry.objects.create(
            date=date,
            description=description,
            reference_type=reference_type,
            reference_id=str(reference_id),
            status='posted'
        )
        
        # Create ledger entries
        for entry in entries:
            account = Account.objects.get(id=entry['account_id'])
            LedgerEntry.objects.create(
                journal_entry=journal_entry,
                account=account,
                debit=Decimal(str(entry.get('debit', 0))),
                credit=Decimal(str(entry.get('credit', 0))),
                description=entry.get('description', '')
            )
        
        # Update account balances
        for entry in entries:
            update_account_balance(Account.objects.get(id=entry['account_id']))
    
    return journal_entry


def get_account_balance(account, as_of_date=None):
    """
    Get account balance.
    
    Args:
        account: Account instance
        as_of_date: Optional date to calculate balance as of (default: today)
    
    Returns:
        Decimal balance
    """
    if as_of_date is None:
        as_of_date = date.today()
    
    # Get cached balance if available and up to date
    try:
        cached_balance = AccountBalance.objects.get(account=account)
        if cached_balance.balance_as_of_date >= as_of_date:
            return cached_balance.net_balance
    except AccountBalance.DoesNotExist:
        pass
    
    # Calculate balance
    return calculate_account_balance(account, as_of_date)


def calculate_account_balance(account, as_of_date=None):
    """
    Calculate account balance from ledger entries.
    
    Args:
        account: Account instance
        as_of_date: Optional date to calculate balance as of (default: today)
    
    Returns:
        Decimal balance (positive for debit balance, negative for credit balance)
    """
    if as_of_date is None:
        as_of_date = date.today()
    
    ledger_entries = LedgerEntry.objects.filter(
        account=account,
        journal_entry__date__lte=as_of_date,
        journal_entry__status='posted'
    )
    
    total_debits = sum(entry.debit for entry in ledger_entries)
    total_credits = sum(entry.credit for entry in ledger_entries)
    
    # For asset and expense accounts, debit balance is positive
    # For liability, equity, and revenue accounts, credit balance is positive
    if account.account_type in ['Asset', 'Expense']:
        balance = total_debits - total_credits
    else:  # Liability, Equity, Revenue
        balance = total_credits - total_debits
    
    return balance


def update_account_balance(account):
    """
    Update cached balance for an account.
    
    Args:
        account: Account instance
    """
    balance = calculate_account_balance(account)
    ledger_entries = LedgerEntry.objects.filter(
        account=account,
        journal_entry__status='posted'
    )
    
    total_debits = sum(entry.debit for entry in ledger_entries)
    total_credits = sum(entry.credit for entry in ledger_entries)
    
    AccountBalance.objects.update_or_create(
        account=account,
        defaults={
            'balance_as_of_date': date.today(),
            'debit_total': total_debits,
            'credit_total': total_credits,
            'net_balance': balance,
            'last_updated': timezone.now()
        }
    )


def update_all_balances():
    """
    Recalculate all cached account balances.
    """
    for account in Account.objects.filter(is_active=True):
        update_account_balance(account)


# Helper functions for external integration

def record_order_payment(order_id, amount, platform_fee, vendor_amount):
    """
    Record order payment transaction.
    
    Uses account numbers from chart of accounts:
    - Cash (1000)
    - Sales Revenue (4000)
    - Platform Fee Expense (5100)
    - Platform Fee Payable (2200)
    - Vendor Payable (2100)
    """
    from datetime import date
    
    # Get accounts by account number
    cash_account = Account.objects.get(account_number='1000')
    sales_revenue = Account.objects.get(account_number='4000')
    platform_fee_expense = Account.objects.get(account_number='5100')
    platform_fee_payable = Account.objects.get(account_number='2200')
    vendor_payable = Account.objects.get(account_number='2100')
    
    # Total amount = vendor_amount + platform_fee
    # Double-entry: Debit Cash, Credit Revenue; Debit Expense, Credit Payables
    entries = [
        {'account_id': cash_account.id, 'debit': amount, 'credit': 0, 'description': 'Cash received'},  # Cash (debit)
        {'account_id': sales_revenue.id, 'debit': 0, 'credit': amount, 'description': 'Sales revenue'},  # Sales Revenue (credit)
        {'account_id': platform_fee_expense.id, 'debit': platform_fee, 'credit': 0, 'description': 'Platform fee expense'},  # Platform Fee Expense (debit)
        {'account_id': platform_fee_payable.id, 'debit': 0, 'credit': platform_fee, 'description': 'Platform fee payable'},  # Platform Fee Payable (credit)
        {'account_id': vendor_payable.id, 'debit': 0, 'credit': vendor_amount, 'description': 'Vendor payable'},  # Vendor Payable (credit)
    ]
    
    return record_transaction(
        date=date.today(),
        description=f'Order payment for order {order_id}',
        reference_type='order',
        reference_id=str(order_id),
        entries=entries
    )


def record_vendor_payout(vendor_id, amount):
    """
    Record vendor payout transaction.
    
    Uses Cash (1000) and Vendor Payable (2100) accounts.
    """
    from datetime import date
    
    cash_account = Account.objects.get(account_number='1000')
    vendor_payable = Account.objects.get(account_number='2100')
    
    entries = [
        {'account_id': vendor_payable.id, 'debit': amount, 'credit': 0, 'description': f'Payout to vendor {vendor_id}'},  # Vendor Payable (debit - reduces liability)
        {'account_id': cash_account.id, 'debit': 0, 'credit': amount, 'description': f'Cash paid to vendor {vendor_id}'}  # Cash (credit - reduces asset)
    ]
    
    return record_transaction(
        date=date.today(),
        description=f'Vendor payout to {vendor_id}',
        reference_type='payment',
        reference_id=str(vendor_id),
        entries=entries
    )


def record_subscription_payment(subscription_id, amount):
    """
    Record subscription payment transaction.
    
    Uses Cash (1000) and Subscription Revenue (4100) accounts.
    """
    from datetime import date
    
    cash_account = Account.objects.get(account_number='1000')
    subscription_revenue = Account.objects.get(account_number='4100')
    
    entries = [
        {'account_id': cash_account.id, 'debit': amount, 'credit': 0, 'description': 'Cash received'},  # Cash (debit)
        {'account_id': subscription_revenue.id, 'debit': 0, 'credit': amount, 'description': 'Subscription revenue'}  # Subscription Revenue (credit)
    ]
    
    return record_transaction(
        date=date.today(),
        description=f'Subscription payment for {subscription_id}',
        reference_type='subscription',
        reference_id=str(subscription_id),
        entries=entries
    )


def record_refund(reference_type, reference_id, amount):
    """
    Record refund transaction (reverse the original transaction).
    """
    from datetime import date
    
    # Get original transaction
    original_entry = JournalEntry.objects.filter(
        reference_type=reference_type,
        reference_id=str(reference_id)
    ).first()
    
    if not original_entry:
        raise ValueError(f"Original transaction not found: {reference_type} {reference_id}")
    
    # Reverse entries
    entries = []
    for ledger_entry in original_entry.ledger_entries.all():
        entries.append({
            'account_id': ledger_entry.account.id,
            'debit': ledger_entry.credit,  # Reverse
            'credit': ledger_entry.debit,  # Reverse
            'description': f'Refund: {ledger_entry.description}'
        })
    
    return record_transaction(
        date=date.today(),
        description=f'Refund for {reference_type} {reference_id}',
        reference_type='refund',
        reference_id=f"{reference_type}_{reference_id}",
        entries=entries
    )

