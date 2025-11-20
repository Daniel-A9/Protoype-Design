from rest_framework import serializers
from .models import Account, JournalEntry, LedgerEntry, AccountBalance


class AccountSerializer(serializers.ModelSerializer):
    balance = serializers.SerializerMethodField()
    
    class Meta:
        model = Account
        fields = ['id', 'account_number', 'account_name', 'account_type', 'normal_balance', 'is_active', 'balance']
        read_only_fields = ['id']
    
    def validate_account_number(self, value):
        """Ensure account number is unique when creating"""
        if self.instance is None:  # Only check on create, not update
            if Account.objects.filter(account_number=value).exists():
                raise serializers.ValidationError("An account with this account number already exists.")
        return value
    
    def get_balance(self, obj):
        try:
            if hasattr(obj, 'balance') and obj.balance:
                return float(obj.balance.net_balance)
            return 0.0
        except (AttributeError, AccountBalance.DoesNotExist, TypeError):
            return 0.0


class LedgerEntrySerializer(serializers.ModelSerializer):
    account_name = serializers.CharField(source='account.account_name', read_only=True)
    account_number = serializers.CharField(source='account.account_number', read_only=True)
    
    class Meta:
        model = LedgerEntry
        fields = ['id', 'account', 'account_name', 'account_number', 'debit', 'credit', 'description']
        read_only_fields = ['id']


class JournalEntrySerializer(serializers.ModelSerializer):
    ledger_entries = LedgerEntrySerializer(many=True, read_only=True)
    total_debits = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    total_credits = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    
    class Meta:
        model = JournalEntry
        fields = ['entry_number', 'date', 'description', 'reference_type', 'reference_id', 'status', 
                  'created_at', 'updated_at', 'ledger_entries', 'total_debits', 'total_credits']
        read_only_fields = ['entry_number', 'created_at', 'updated_at']


class TransactionCreateSerializer(serializers.Serializer):
    """Serializer for creating transactions via API"""
    date = serializers.DateField()
    description = serializers.CharField(max_length=500)
    reference_type = serializers.CharField(max_length=50)
    reference_id = serializers.CharField(max_length=100)
    entries = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )
    
    def validate_entries(self, value):
        if not value or len(value) < 2:
            raise serializers.ValidationError("A transaction must have at least two entries")
        return value
    
    def validate(self, data):
        entries = data['entries']
        total_debits = sum(float(e.get('debit', 0)) for e in entries)
        total_credits = sum(float(e.get('credit', 0)) for e in entries)
        
        if abs(total_debits - total_credits) > 0.01:  # Allow small rounding differences
            raise serializers.ValidationError(
                f"Debits ({total_debits}) must equal credits ({total_credits})"
            )
        
        return data


class AccountBalanceSerializer(serializers.ModelSerializer):
    account_name = serializers.CharField(source='account.account_name', read_only=True)
    account_number = serializers.CharField(source='account.account_number', read_only=True)
    
    class Meta:
        model = AccountBalance
        fields = ['account', 'account_name', 'account_number', 'balance_as_of_date', 
                  'debit_total', 'credit_total', 'net_balance', 'last_updated']

