# Stripe Integration Setup Guide

## 🔧 **Step 1: Create Stripe Account**

1. Go to [https://stripe.com](https://stripe.com) and create an account
2. Complete account verification
3. Switch to **Test Mode** for development

## 🔑 **Step 2: Get API Keys**

1. Go to **Developers → API keys**
2. Copy your **Publishable key** (starts with `pk_test_`)
3. Copy your **Secret key** (starts with `sk_test_`)

## 💰 **Step 3: Create Products and Prices**

### Create Pro Plan:
1. Go to **Products → Add product**
2. **Name:** `WebCammer+ Pro`
3. **Pricing model:** `Recurring`
4. **Price:** `$9.99 USD`
5. **Billing period:** `Monthly`
6. **Save** and copy the **Price ID** (starts with `price_`)

### Create Pro Yearly:
1. **Add another price** to the Pro product
2. **Price:** `$99.99 USD`
3. **Billing period:** `Yearly`
4. **Save** and copy the **Price ID**

### Create Max Plan:
1. **Create new product:** `WebCammer+ Max`
2. **Price:** `$29.99 USD Monthly`
3. **Add yearly price:** `$299.99 USD Yearly`
4. **Save both Price IDs**

## 🔗 **Step 4: Set Up Webhooks**

1. Go to **Developers → Webhooks**
2. **Add endpoint**
3. **Endpoint URL:** `http://localhost:5000/api/v1/subscription/webhook`
4. **Select events:**
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. **Add endpoint** and copy the **Signing secret** (starts with `whsec_`)

## 🌐 **Step 5: Configure Environment Variables**

Create `/server/.env` file:

```bash
# Auth0
AUTH0_DOMAIN=dev-4xh5xi1xfh7w7y2n.us.auth0.com
AUTH0_CLIENT_ID=57sIYSODLSDddlyQVokooAFjTEHDNRYo
AUTH0_CLIENT_SECRET=your-auth0-client-secret
AUTH0_AUDIENCE=https://dev-4xh5xi1xfh7w7y2n.us.auth0.com/api/v2/

# Stripe (replace with your actual keys)
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here

# Stripe Price IDs (replace with your actual price IDs)
STRIPE_PRICE_PRO_MONTHLY=price_your_pro_monthly_id
STRIPE_PRICE_PRO_YEARLY=price_your_pro_yearly_id
STRIPE_PRICE_MAX_MONTHLY=price_your_max_monthly_id
STRIPE_PRICE_MAX_YEARLY=price_your_max_yearly_id

# Flask
FLASK_SECRET_KEY=your-super-secret-flask-key-here
```

## 🧪 **Step 6: Test the Integration**

1. **Start your Flask server:**
   ```bash
   cd server
   python app.py
   ```

2. **Open the subscription page:**
   ```
   http://localhost:3000/subscription.html
   ```

3. **Test the flow:**
   - Click "Upgrade to Pro"
   - Should redirect to Stripe Checkout
   - Use test card: `4242 4242 4242 4242`
   - Any future date for expiry
   - Any 3-digit CVC

## 🎯 **Step 7: Test Webhooks (Optional)**

Use Stripe CLI for local webhook testing:

1. **Install Stripe CLI**
2. **Login:** `stripe login`
3. **Forward webhooks:** 
   ```bash
   stripe listen --forward-to localhost:5000/api/v1/subscription/webhook
   ```

## 📱 **What Happens After Setup:**

1. ✅ **Users can subscribe** to Pro/Max plans
2. ✅ **Stripe handles payments** securely
3. ✅ **Webhooks update** user subscriptions automatically
4. ✅ **Usage limits** are enforced based on subscription tier
5. ✅ **Users can manage billing** through Stripe portal

## 🚨 **Important Notes:**

- **Use test mode** during development
- **Never commit** real API keys to version control
- **Webhooks are required** for subscription status updates
- **Test thoroughly** before going live

## 🆘 **Troubleshooting:**

- **"No such price"** → Check Price IDs in environment variables
- **Webhook errors** → Verify endpoint URL and signing secret
- **Auth errors** → Ensure user is logged in with Auth0
- **CORS issues** → Check Flask-CORS configuration

Your Stripe integration should now be fully functional! 🎉