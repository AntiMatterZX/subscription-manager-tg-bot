from flask import Blueprint, request, jsonify
from sqlalchemy import and_
from app.models import User, Subscription, Product, TelegramGroup

user_bp = Blueprint('user', __name__)


def _serialize_member(sub: Subscription):
    return {
        'subscription_id': sub.id,
        'status': sub.status,
        'subscription_expires_at': sub.subscription_expires_at,
        'invite_link_url': sub.invite_link_url,
        'invite_link_expires_at': sub.invite_link_expires_at,
        'user': {
            'id': sub.user.id,
            'email': sub.user.email,
            'telegram_user_id': sub.user.telegram_user_id,
            'telegram_username': sub.user.telegram_username,
        },
        'product': {
            'id': sub.product.id,
            'name': sub.product.name,
            'description': sub.product.description,
        },
        'telegram_group': {
            'id': sub.telegram_group.id,
            'telegram_group_id': sub.telegram_group.telegram_group_id,
            'telegram_group_name': sub.telegram_group.telegram_group_name,
            'is_active': sub.telegram_group.is_active,
        },
    }


@user_bp.route('/users/joined', methods=['GET'])
def list_joined_users():
    """
    List users who joined via invite link (users with recorded telegram_user_id) with mapping context.
    Optional query params:
      - product_id (string)
      - telegram_group_id (string)
      - status (comma-separated: pending_join,active,expired,cancelled)
    """
    product_id = request.args.get('product_id')
    telegram_group_id = request.args.get('telegram_group_id')
    status_param = request.args.get('status')

    q = Subscription.query.join(User).join(Product).outerjoin(TelegramGroup)

    # Only subscriptions where we have a telegram_user_id recorded
    q = q.filter(User.telegram_user_id.isnot(None))

    if product_id:
        q = q.filter(Subscription.product_id == product_id)

    if telegram_group_id:
        q = q.filter(TelegramGroup.telegram_group_id == str(telegram_group_id))

    if status_param:
        statuses = [s.strip() for s in status_param.split(',') if s.strip()]
        if statuses:
            q = q.filter(Subscription.status.in_(statuses))

    subs = q.all()
    return jsonify([_serialize_member(s) for s in subs]), 200


@user_bp.route('/products/<string:product_id>/members', methods=['GET'])
def list_product_members(product_id: str):
    """Convenience endpoint: list members for a given product (by string product_id)."""
    q = (
        Subscription.query.join(User).join(Product).outerjoin(TelegramGroup)
        .filter(Subscription.product_id == product_id)
        .filter(User.telegram_user_id.isnot(None))
    )
    subs = q.all()
    return jsonify([_serialize_member(s) for s in subs]), 200


@user_bp.route('/groups/<string:telegram_group_id>/members', methods=['GET'])
def list_group_members(telegram_group_id: str):
    """Convenience endpoint: list members for a given Telegram group id."""
    q = (
        Subscription.query.join(User).join(Product).outerjoin(TelegramGroup)
        .filter(TelegramGroup.telegram_group_id == str(telegram_group_id))
        .filter(User.telegram_user_id.isnot(None))
    )
    subs = q.all()
    return jsonify([_serialize_member(s) for s in subs]), 200
