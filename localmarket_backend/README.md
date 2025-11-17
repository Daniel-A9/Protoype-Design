# LocalMarket Backend - Django Ledger

A simple, essential accounting ledger system for small business use. This Django backend provides double-entry bookkeeping functionality with a REST API for external systems (orders, payments, subscriptions) to record financial transactions.

## Features

- **Double-Entry Bookkeeping**: All transactions follow accounting principles (debits = credits)
- **Simple API**: Easy-to-use REST endpoints for recording transactions
- **Chart of Accounts**: Pre-configured accounts for marketplace operations
- **Financial Reports**: Trial balance, profit & loss, and balance sheet
- **Flexible Integration**: External systems connect via API with string-based references (no FK constraints)
- **Django Admin**: Full admin interface for managing accounts and transactions

## Project Structure

```
localmarket_backend/
├── ledger/                 # Ledger Django app
│   ├── models.py          # Account, JournalEntry, LedgerEntry, AccountBalance
│   ├── services.py        # Business logic for transactions
│   ├── views.py           # REST API views
│   ├── serializers.py     # DRF serializers
│   ├── admin.py           # Django admin configuration
│   └── urls.py            # API URL routing
├── localmarket_backend/   # Django project settings
└── manage.py             # Django management script
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Navigate to the project directory:**
   ```bash
   cd localmarket_backend
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (optional, for admin access):**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/api/ledger/`
The Django admin will be available at `http://localhost:8000/admin/`

## API Documentation

### Base URL
```
http://localhost:8000/api/ledger/
```

### Endpoints

#### Accounts

**List all accounts:**
```http
GET /api/ledger/accounts/
```

**Get account details:**
```http
GET /api/ledger/accounts/{id}/
```

**Get account balance:**
```http
GET /api/ledger/accounts/{id}/balance/?as_of_date=2024-01-15
```

Response:
```json
{
  "account": "Cash",
  "account_number": "1000",
  "balance": 15000.00,
  "as_of_date": "2024-01-15"
}
```

#### Transactions

**Create a transaction:**
```http
POST /api/ledger/transactions/
Content-Type: application/json

{
  "date": "2024-01-15",
  "description": "Order payment for order #12345",
  "reference_type": "order",
  "reference_id": "12345",
  "entries": [
    {
      "account_id": 1,
      "debit": 100.00,
      "credit": 0,
      "description": "Cash received"
    },
    {
      "account_id": 4,
      "debit": 0,
      "credit": 100.00,
      "description": "Sales revenue"
    }
  ]
}
```

**List transactions (with filters):**
```http
GET /api/ledger/transactions/?reference_type=order&reference_id=12345&date_from=2024-01-01&date_to=2024-01-31
```

Query parameters:
- `reference_type`: Filter by reference type (order, payment, subscription, refund, manual)
- `reference_id`: Filter by reference ID
- `date_from`: Filter transactions from this date (YYYY-MM-DD)
- `date_to`: Filter transactions to this date (YYYY-MM-DD)

#### Reports

**Trial Balance:**
```http
GET /api/ledger/reports/trial-balance/?as_of_date=2024-01-31
```

**Profit & Loss:**
```http
GET /api/ledger/reports/profit-loss/?date_from=2024-01-01&date_to=2024-01-31
```

**Balance Sheet:**
```http
GET /api/ledger/reports/balance-sheet/?as_of_date=2024-01-31
```

## Chart of Accounts

The system comes pre-configured with essential accounts:

### Assets (Debit Normal Balance)
- **1000** - Cash
- **1100** - Bank Account
- **1200** - Accounts Receivable

### Liabilities (Credit Normal Balance)
- **2000** - Accounts Payable
- **2100** - Vendor Payables
- **2200** - Platform Fee Payable

### Equity (Credit Normal Balance)
- **3000** - Owner's Equity
- **3100** - Retained Earnings

### Revenue (Credit Normal Balance)
- **4000** - Sales Revenue
- **4100** - Subscription Revenue

### Expenses (Debit Normal Balance)
- **5000** - Operating Expenses
- **5100** - Platform Fee Expense
- **5200** - Cost of Goods Sold

## Integration Guide

### Recording Transactions from External Systems

External systems (orders, payments, products) remain independent and connect to the ledger via API. The ledger stores `reference_type` and `reference_id` as strings for flexibility.

#### Example: Recording an Order Payment

When an order payment completes in your order system:

```python
import requests

# Your order system receives payment
order_id = "12345"
total_amount = 100.00
platform_fee = 10.00
vendor_amount = 90.00

# Record in ledger
response = requests.post('http://localhost:8000/api/ledger/transactions/', json={
    "date": "2024-01-15",
    "description": f"Order payment for order #{order_id}",
    "reference_type": "order",
    "reference_id": str(order_id),
    "entries": [
        {
            "account_id": 1,  # Cash (get from GET /api/ledger/accounts/)
            "debit": total_amount,
            "credit": 0,
            "description": "Cash received"
        },
        {
            "account_id": 4,  # Sales Revenue
            "debit": 0,
            "credit": total_amount,
            "description": "Sales revenue"
        },
        {
            "account_id": 6,  # Platform Fee Expense
            "debit": platform_fee,
            "credit": 0,
            "description": "Platform fee"
        },
        {
            "account_id": 5,  # Platform Fee Payable
            "debit": 0,
            "credit": platform_fee,
            "description": "Platform fee payable"
        },
        {
            "account_id": 3,  # Vendor Payable
            "debit": 0,
            "credit": vendor_amount,
            "description": "Vendor payable"
        }
    ]
})
```

#### Example: Recording a Vendor Payout

When you pay out money to a vendor:

```python
vendor_id = "vendor_123"
payout_amount = 90.00

response = requests.post('http://localhost:8000/api/ledger/transactions/', json={
    "date": "2024-01-20",
    "description": f"Vendor payout to {vendor_id}",
    "reference_type": "payment",
    "reference_id": str(vendor_id),
    "entries": [
        {
            "account_id": 3,  # Vendor Payable (reduce liability)
            "debit": payout_amount,
            "credit": 0,
            "description": f"Payout to vendor {vendor_id}"
        },
        {
            "account_id": 1,  # Cash (reduce asset)
            "debit": 0,
            "credit": payout_amount,
            "description": f"Cash paid to vendor {vendor_id}"
        }
    ]
})
```

### Using Helper Functions (Python)

If your external system is also Python-based, you can import and use helper functions:

```python
from ledger.services import (
    record_order_payment,
    record_vendor_payout,
    record_subscription_payment,
    record_refund
)

# Record order payment
record_order_payment(
    order_id="12345",
    amount=100.00,
    platform_fee=10.00,
    vendor_amount=90.00
)

# Record vendor payout
record_vendor_payout(
    vendor_id="vendor_123",
    amount=90.00
)

# Record subscription payment
record_subscription_payment(
    subscription_id="sub_456",
    amount=29.99
)

# Record refund
record_refund(
    reference_type="order",
    reference_id="12345",
    amount=100.00
)
```

## Django Admin

Access the admin interface at `http://localhost:8000/admin/` after creating a superuser.

**Features:**
- View and manage chart of accounts
- Create journal entries with inline ledger entries
- View account balances
- Browse transaction history
- Validate debits = credits when saving entries

## Important Notes

### Double-Entry Bookkeeping

Every transaction must have balanced debits and credits. The system validates this automatically.

**Rules:**
- **Assets** and **Expenses**: Debit increases, Credit decreases
- **Liabilities**, **Equity**, and **Revenue**: Credit increases, Debit decreases

### Reference Types

Use consistent `reference_type` values for filtering:
- `order` - Order-related transactions
- `payment` - Payment transactions
- `subscription` - Subscription transactions
- `refund` - Refund transactions
- `manual` - Manually created transactions

### Account IDs

Account IDs are auto-generated. To get account IDs, first call `GET /api/ledger/accounts/` to list all accounts and their IDs.

Alternatively, use the helper functions which look up accounts by account number automatically.

## Development

### Running Tests

```bash
python manage.py test
```

### Creating Migrations

```bash
python manage.py makemigrations
```

### Applying Migrations

```bash
python manage.py migrate
```

### Recalculating All Balances

```bash
python manage.py shell
```

```python
from ledger.services import update_all_balances
update_all_balances()
```

## Production Considerations

1. **Security**: Change `DEBUG=False` and set proper `SECRET_KEY` and `ALLOWED_HOSTS` in `settings.py`
2. **Database**: Use PostgreSQL for production (update `DATABASES` in `settings.py`)
3. **Authentication**: Implement proper authentication/authorization (update `REST_FRAMEWORK` settings)
4. **CORS**: Configure `CORS_ALLOWED_ORIGINS` for your production frontend domains
5. **Environment Variables**: Use `python-decouple` to manage settings from `.env` file

## License

This project is part of the LocalMarket platform.

