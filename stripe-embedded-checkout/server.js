import express from "express";
import Stripe from "stripe";
import dotenv from "dotenv";

dotenv.config();

const app = express();
const port = process.env.PORT || 4242;

if (!process.env.STRIPE_SECRET_KEY) {
  console.warn("Warning: STRIPE_SECRET_KEY is not set. API calls will fail until it is provided.");
}

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY ?? "");

app.use(express.static("public"));
app.use(express.json());

app.get("/config", (req, res) => {
  if (!process.env.STRIPE_PUBLISHABLE_KEY) {
    return res.status(500).json({
      error: "Stripe publishable key is not configured."
    });
  }

  res.json({
    publishableKey: process.env.STRIPE_PUBLISHABLE_KEY
  });
});

app.post("/create-checkout-session", async (req, res) => {
  try {
    const priceId = process.env.STRIPE_PRICE_ID;

    if (!priceId) {
      return res.status(400).json({ error: "STRIPE_PRICE_ID must be configured." });
    }

    const session = await stripe.checkout.sessions.create({
      ui_mode: "embedded",
      mode: "subscription",
      line_items: [
        {
          price: priceId,
          quantity: 1
        }
      ],
      return_url: `${req.protocol}://${req.get("host")}/return.html?session_id={CHECKOUT_SESSION_ID}`
    });

    res.json({ clientSecret: session.client_secret });
  } catch (error) {
    console.error("Stripe error:", error);
    res.status(500).json({ error: error.message });
  }
});

app.get("/session-status", async (req, res) => {
  try {
    const { session_id: sessionId } = req.query;

    if (!sessionId) {
      return res.status(400).json({ error: "session_id query parameter is required." });
    }

    const session = await stripe.checkout.sessions.retrieve(sessionId);

    res.json({
      status: session.status,
      customer_email: session.customer_details?.email,
      subscription: session.subscription
    });
  } catch (error) {
    console.error("Session status error:", error);
    res.status(500).json({ error: error.message });
  }
});

app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}`);
});
