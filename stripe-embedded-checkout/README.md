# Stripe Embedded Checkout Demo

This project provides a minimal Express server and static client to test Stripe's Embedded Checkout experience with your test credentials.

## Prerequisites

- Node.js 18+
- Stripe test mode API keys and a recurring price ID

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```
2. Copy `env.example` to `.env` and fill in your Stripe test values:
   - `STRIPE_SECRET_KEY`
   - `STRIPE_PUBLISHABLE_KEY`
   - `STRIPE_PRICE_ID`
   - `STRIPE_WEBHOOK_SECRET` (optional for future webhook tests)
   - `PORT` (defaults to `4242` if omitted)

## Run the server

```bash
npm start
```

Visit `http://localhost:4242` to load the embedded checkout demo. The page fetches the publishable key from the server, creates a Checkout Session, and mounts the embedded checkout interface.

## Test payments

Use Stripe's test card numbers (for example, `4242 4242 4242 4242` with any future expiry and CVC) to simulate successful payments. After completing checkout, you are redirected to `return.html`, which calls `/session-status` to display the Checkout Session state.

## Next steps

- Connect the optional webhook endpoint for subscription lifecycle testing.
- Replace the static line item price with dynamic logic for multiple plans or seat counts.
- Integrate success/error handling into your application flow once you move beyond testing.
