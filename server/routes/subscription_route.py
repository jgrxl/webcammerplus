from flask import Response, abort, jsonify, request
from flask_restx import Namespace, Resource, fields
from utils.auth import requires_auth
from services.user_service import UserService
from services.stripe_service import StripeService
from models.subscription_tiers import SubscriptionTier, get_tier_by_name
import stripe


api = Namespace('subscription', description='Subscription management')

# Request models
checkout_request_model = api.model('CheckoutRequest', {
    'tier': fields.String(required=True, description='Subscription tier (pro, max)', enum=['pro', 'max']),
    'billing_cycle': fields.String(required=True, description='Billing cycle', enum=['monthly', 'yearly'], default='monthly'),
    'success_url': fields.String(required=True, description='URL to redirect after successful payment'),
    'cancel_url': fields.String(required=True, description='URL to redirect if payment is cancelled')
})

# Response models
checkout_response_model = api.model('CheckoutResponse', {
    'checkout_url': fields.String(description='Stripe Checkout session URL'),
    'session_id': fields.String(description='Stripe Checkout session ID')
})

billing_portal_response_model = api.model('BillingPortalResponse', {
    'portal_url': fields.String(description='Stripe billing portal URL')
})

subscription_response_model = api.model('SubscriptionResponse', {
    'tier': fields.String(description='Current subscription tier'),
    'status': fields.String(description='Subscription status'),
    'billing_cycle': fields.String(description='Billing cycle'),
    'current_period_start': fields.String(description='Current period start date'),
    'current_period_end': fields.String(description='Current period end date'),
    'cancel_at_period_end': fields.Boolean(description='Whether subscription will cancel at period end'),
    'amount': fields.Float(description='Subscription amount'),
    'currency': fields.String(description='Currency code')
})

error_model = api.model('Error', {
    'error': fields.String(description='Error message')
})


@api.route('/checkout')
class CreateCheckout(Resource):
    @api.expect(checkout_request_model)
    @api.response(200, 'Success', checkout_response_model)
    @api.response(400, 'Bad Request', error_model)
    @api.response(401, 'Unauthorized', error_model)
    @api.doc('create_checkout_session')
    @requires_auth
    def post(self):
        """Create Stripe checkout session for subscription"""
        try:
            user = request.user
            payload = request.get_json(force=True) or {}
            
            # Validate request
            tier_name = payload.get('tier')
            billing_cycle = payload.get('billing_cycle', 'monthly')
            success_url = payload.get('success_url')
            cancel_url = payload.get('cancel_url')
            
            if not all([tier_name, success_url, cancel_url]):
                return jsonify({'error': 'Missing required fields'}), 400
            
            # Validate tier
            tier = get_tier_by_name(tier_name)
            if not tier or tier == SubscriptionTier.FREE:
                return jsonify({'error': 'Invalid subscription tier'}), 400
            
            # Validate billing cycle
            if billing_cycle not in ['monthly', 'yearly']:
                return jsonify({'error': 'Invalid billing cycle'}), 400
            
            # Check if user already has an active subscription
            if user.subscription_tier != SubscriptionTier.FREE and user.is_subscription_active():
                return jsonify({'error': 'User already has an active subscription'}), 400
            
            # Ensure user has Stripe customer ID
            if not user.stripe_customer_id:
                stripe_service = StripeService()
                customer = stripe_service.create_customer(
                    user_email=user.email,
                    user_name=user.name,
                    auth0_id=user.auth0_id
                )
                
                # Update user with customer ID
                user_service = UserService()
                user_service.update_user_subscription(
                    user.auth0_id,
                    user.subscription_tier,
                    stripe_customer_id=customer.id
                )
                user.stripe_customer_id = customer.id
            
            # Create checkout session
            stripe_service = StripeService()
            session = stripe_service.create_checkout_session(
                customer_id=user.stripe_customer_id,
                tier=tier,
                billing_cycle=billing_cycle,
                success_url=success_url,
                cancel_url=cancel_url
            )
            
            return jsonify({
                'checkout_url': session.url,
                'session_id': session.id
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500


@api.route('/billing-portal')
class BillingPortal(Resource):
    @api.response(200, 'Success', billing_portal_response_model)
    @api.response(400, 'Bad Request', error_model)
    @api.response(401, 'Unauthorized', error_model)
    @api.doc('create_billing_portal_session')
    @requires_auth
    def post(self):
        """Create Stripe billing portal session"""
        try:
            user = request.user
            payload = request.get_json(force=True) or {}
            return_url = payload.get('return_url', '')
            
            if not user.stripe_customer_id:
                return jsonify({'error': 'No Stripe customer found'}), 400
            
            stripe_service = StripeService()
            session = stripe_service.create_billing_portal_session(
                customer_id=user.stripe_customer_id,
                return_url=return_url
            )
            
            return jsonify({
                'portal_url': session.url
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500


@api.route('/status')
class SubscriptionStatus(Resource):
    @api.response(200, 'Success', subscription_response_model)
    @api.response(401, 'Unauthorized', error_model)
    @api.doc('get_subscription_status')
    @requires_auth
    def get(self):
        """Get current subscription status"""
        try:
            user = request.user
            
            if user.subscription_tier == SubscriptionTier.FREE:
                return jsonify({
                    'tier': 'free',
                    'status': 'active',
                    'billing_cycle': None,
                    'current_period_start': None,
                    'current_period_end': None,
                    'cancel_at_period_end': False,
                    'amount': 0.0,
                    'currency': 'usd'
                })
            
            # Get subscription details from Stripe
            if user.stripe_customer_id:
                stripe_service = StripeService()
                subscriptions = stripe_service.get_customer_subscriptions(user.stripe_customer_id)
                
                if subscriptions:
                    # Get the most recent active subscription
                    active_sub = None
                    for sub in subscriptions:
                        if sub.status in ['active', 'trialing', 'past_due']:
                            active_sub = sub
                            break
                    
                    if active_sub:
                        return jsonify({
                            'tier': user.subscription_tier.value,
                            'status': active_sub.status,
                            'billing_cycle': active_sub.metadata.get('billing_cycle', 'monthly'),
                            'current_period_start': active_sub.current_period_start,
                            'current_period_end': active_sub.current_period_end,
                            'cancel_at_period_end': active_sub.cancel_at_period_end,
                            'amount': active_sub.items.data[0].price.unit_amount / 100,
                            'currency': active_sub.items.data[0].price.currency
                        })
            
            # Fallback to user data
            return jsonify({
                'tier': user.subscription_tier.value,
                'status': user.subscription_status,
                'billing_cycle': None,
                'current_period_start': user.subscription_start_date.isoformat() if user.subscription_start_date else None,
                'current_period_end': user.subscription_end_date.isoformat() if user.subscription_end_date else None,
                'cancel_at_period_end': False,
                'amount': 0.0,
                'currency': 'usd'
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500


@api.route('/cancel')
class CancelSubscription(Resource):
    @api.response(200, 'Success')
    @api.response(400, 'Bad Request', error_model)
    @api.response(401, 'Unauthorized', error_model)
    @api.doc('cancel_subscription')
    @requires_auth
    def post(self):
        """Cancel current subscription (at period end)"""
        try:
            user = request.user
            
            if user.subscription_tier == SubscriptionTier.FREE:
                return jsonify({'error': 'No active subscription to cancel'}), 400
            
            if not user.stripe_customer_id:
                return jsonify({'error': 'No Stripe customer found'}), 400
            
            # Find active subscription
            stripe_service = StripeService()
            subscriptions = stripe_service.get_customer_subscriptions(user.stripe_customer_id)
            
            active_sub = None
            for sub in subscriptions:
                if sub.status in ['active', 'trialing']:
                    active_sub = sub
                    break
            
            if not active_sub:
                return jsonify({'error': 'No active subscription found'}), 400
            
            # Cancel subscription at period end
            cancelled_sub = stripe_service.cancel_subscription(active_sub.id, at_period_end=True)
            
            return jsonify({
                'message': 'Subscription will be cancelled at the end of the current period',
                'cancel_at_period_end': cancelled_sub.cancel_at_period_end,
                'current_period_end': cancelled_sub.current_period_end
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500


@api.route('/webhook')
class StripeWebhook(Resource):
    @api.doc(False)  # Hide from Swagger docs
    def post(self):
        """Handle Stripe webhook events"""
        try:
            payload = request.get_data()
            signature = request.headers.get('Stripe-Signature')
            
            stripe_service = StripeService()
            
            # Skip signature verification in development if no webhook secret is configured
            if signature and stripe_service.webhook_secret:
                # Verify webhook signature
                if not stripe_service.verify_webhook_signature(payload, signature):
                    return jsonify({'error': 'Invalid signature'}), 400
            else:
                print("⚠️  Webhook signature verification skipped (development mode)")
            
            # Parse event
            try:
                event = stripe.Event.construct_from(
                    stripe.util.convert_to_stripe_object(request.get_json()),
                    stripe.api_key
                )
            except ValueError:
                return jsonify({'error': 'Invalid payload'}), 400
            
            # Process event
            subscription_data = stripe_service.process_webhook_event(event.to_dict())
            
            if subscription_data:
                # Update user subscription in our system
                user_service = UserService()
                
                # Find user by Stripe customer ID
                stripe_customer_id = subscription_data.stripe_customer_id
                
                # Get customer from Stripe to find Auth0 ID
                customer = stripe_service.get_customer(stripe_customer_id)
                if customer and customer.metadata.get('auth0_id'):
                    auth0_id = customer.metadata['auth0_id']
                    
                    # Update user subscription
                    user_service.update_user_subscription(
                        auth0_id=auth0_id,
                        tier=subscription_data.tier,
                        stripe_customer_id=stripe_customer_id,
                        subscription_start=subscription_data.current_period_start,
                        subscription_end=subscription_data.current_period_end,
                        status=subscription_data.status
                    )
                    
                    # Store subscription record
                    subscription_data.user_auth0_id = auth0_id
                    user_service.create_subscription(subscription_data)
            
            return jsonify({'status': 'success'})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500