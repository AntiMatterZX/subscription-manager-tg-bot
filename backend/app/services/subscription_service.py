from datetime import datetime, timedelta
from app import db
from app.models import User, Product, TelegramGroup, Subscription
from sqlalchemy.exc import SQLAlchemyError
from app.bot.telegram_client import generate_invite_link
from app.services.telegram import tg_bot


class SubscriptionService:
    @staticmethod
    def get_all_subscriptions():
        return Subscription.query.all()

    @staticmethod
    def get_subscription_by_id(subscription_id):
        return Subscription.query.get(subscription_id)

    @staticmethod
    def get_subscription_by_invite_token(invite_token):
        return Subscription.query.filter_by(invite_link_token=invite_token).first()

    @staticmethod
    def get_active_subscriptions_by_user_id(user_id):
        return Subscription.query.filter_by(user_id=user_id, status="active").all()

    @staticmethod
    def get_expired_subscriptions():
        now = datetime.utcnow()
        return Subscription.query.filter(
            Subscription.status == "active", Subscription.subscription_expires_at <= now
        ).all()

    @staticmethod
    def create_subsciption_by_product_name(email, product_name):
        product = Product.query.filter_by(name=product_name).first()
        if not product:
            return None, "Product not found"
        return SubscriptionService.create_subscription(email, product.id)

    @staticmethod
    def create_subscription(email, product_id):
        try:
            # Check if product exists and has a mapped group
            product = Product.query.get(product_id)
            if not product:
                return None, "Product not found"

            if not product.telegram_group:
                return None, "Product is not mapped to a Telegram group"

            # Get or create user
            user = User.query.filter_by(email=email).first()
            if not user:
                user = User(email=email)
                db.session.add(user)
                db.session.flush()  # Get user ID without committing

            # Check if user already has an active subscription for this product
            existing_subscription = Subscription.query.filter_by(
                user_id=user.id, product_id=product_id, status="active"
            ).first()

            if existing_subscription:
                return None, "User already has an active subscription for this product"

            # Create subscription (default expiry is 30 days)
            subscription_expires_at = datetime.utcnow() + timedelta(days=30)
            subscription = Subscription(
                user_id=user.id,
                product_id=product_id,
                telegram_group_id=product.telegram_group.id,
                subscription_starts_at=datetime.utcnow(),
                subscription_expires_at=subscription_expires_at,
                status="pending_join",
            )
            db.session.add(subscription)
            db.session.flush()  # Get subscription ID without committing

            # Generate invite link (valid for 24 hours)
            invite_link_expires_at = datetime.utcnow() + timedelta(hours=24)
            import uuid

            invite_token = str(uuid.uuid4())
            success, invite_link = tg_bot.create_invite_link(
                product.telegram_group.telegram_group_id, invite_token, user.id
            )

            if not success or not invite_link:
                db.session.rollback()
                return None, "Failed to generate invite link"

            subscription.invite_link_url = invite_link
            subscription.invite_link_token = invite_token
            subscription.invite_link_expires_at = invite_link_expires_at

            db.session.commit()
            return subscription, None
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    @staticmethod
    def update_subscription_with_telegram_user(
        invite_token, telegram_user_id, telegram_username
    ):
        try:
            subscription = Subscription.query.filter_by(
                invite_link_token=invite_token
            ).first()
            if not subscription:
                return None, "Subscription not found"

            # Update user with Telegram information
            user = subscription.user
            user.telegram_user_id = telegram_user_id
            user.telegram_username = telegram_username

            # Update subscription status
            subscription.status = "active"

            db.session.commit()
            return subscription, None
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    @staticmethod
    def expire_subscription(subscription_id):
        try:
            subscription = Subscription.query.get(subscription_id)
            if not subscription:
                return False

            subscription.status = "expired"
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e
