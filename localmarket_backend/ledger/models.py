from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Account(models.Model):
    """
    Chart of Accounts - Account model
    """
    ACCOUNT_TYPES = [
        ('Asset', 'Asset'),
        ('Liability', 'Liability'),
        ('Equity', 'Equity'),
        ('Revenue', 'Revenue'),
        ('Expense', 'Expense'),
    ]
    
    NORMAL_BALANCE_CHOICES = [
        ('Debit', 'Debit'),
        ('Credit', 'Credit'),
    ]
    
    account_number = models.CharField(max_length=20, unique=True, help_text="Chart of accounts code")
    account_name = models.CharField(max_length=200)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    normal_balance = models.CharField(max_length=10, choices=NORMAL_BALANCE_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['account_number']
    
    def __str__(self):
        return f"{self.account_number} - {self.account_name}"


class JournalEntry(models.Model):
    """
    Journal Entry - Groups related ledger entries
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('posted', 'Posted'),
    ]
    
    entry_number = models.AutoField(primary_key=True)
    date = models.DateField()
    description = models.CharField(max_length=500)
    reference_type = models.CharField(
        max_length=50,
        help_text="External system identifier: order, payment, subscription, refund, manual"
    )
    reference_id = models.CharField(
        max_length=100,
        help_text="External system's ID (string, no FK constraint for flexibility)"
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-entry_number']
        verbose_name_plural = "Journal Entries"
        indexes = [
            models.Index(fields=['reference_type', 'reference_id']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"Entry #{self.entry_number} - {self.description} ({self.date})"
    
    @property
    def total_debits(self):
        return sum(entry.debit for entry in self.ledger_entries.all())
    
    @property
    def total_credits(self):
        return sum(entry.credit for entry in self.ledger_entries.all())


class LedgerEntry(models.Model):
    """
    Ledger Entry - Individual line items in a journal entry
    """
    journal_entry = models.ForeignKey(
        JournalEntry,
        on_delete=models.CASCADE,
        related_name='ledger_entries'
    )
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    debit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    credit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    description = models.CharField(max_length=500, blank=True)
    
    class Meta:
        ordering = ['journal_entry', 'id']
        verbose_name_plural = "Ledger Entries"
        indexes = [
            models.Index(fields=['account', 'journal_entry']),
        ]
    
    def __str__(self):
        amount = self.debit if self.debit > 0 else self.credit
        dr_cr = 'DR' if self.debit > 0 else 'CR'
        return f"{self.account.account_name} - {amount} {dr_cr}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.debit > 0 and self.credit > 0:
            raise ValidationError("An entry cannot have both debit and credit amounts")
        if self.debit == 0 and self.credit == 0:
            raise ValidationError("An entry must have either a debit or credit amount")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class AccountBalance(models.Model):
    """
    Cached account balances for performance
    """
    account = models.OneToOneField(
        Account,
        on_delete=models.CASCADE,
        related_name='balance'
    )
    balance_as_of_date = models.DateField()
    debit_total = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    credit_total = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    net_balance = models.DecimalField(max_digits=15, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['account']
    
    def __str__(self):
        return f"{self.account.account_name} - Balance: {self.net_balance}"
