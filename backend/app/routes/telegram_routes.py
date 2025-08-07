import os
import logging
from flask import Blueprint, request, jsonify
from app.bot.telegram_handler import process_update
from app.bot.telegram_client import get_bot
from app.services.telegram import tg_bot
from app.models import Product, TelegramGroup, User, Subscription

# Configure logging
logger = logging.getLogger(__name__)

telegram_bp = Blueprint('telegram', __name__)

@telegram_bp.route('/telegram/webhook/<token>', methods=['POST'])
def telegram_webhook(token):
    # Verify the token
    if token != os.environ.get('TELEGRAM_BOT_TOKEN'):
        logger.warning(f"Invalid token received in webhook: {token}")
        return jsonify({'message': 'Invalid token'}), 401
    
    # Check if we're using webhooks
    from app.bot import USE_WEBHOOKS
    if not USE_WEBHOOKS:
        logger.info("Webhook received but system is configured to use handlers instead")
        return jsonify({'message': 'System is using handlers, not webhooks'}), 200
    
    # Process the update
    try:
        update = request.json
        logger.info(f"Received Telegram update: {update}")
        process_update(update)
        return jsonify({'message': 'Update processed successfully'}), 200
    except Exception as e:
        logger.error(f"Error processing Telegram update: {e}")
        return jsonify({'message': f'Error processing update: {str(e)}'}), 500

@telegram_bp.route('/telegram/webhook/test', methods=['GET'])
def test_webhook():
    """Test endpoint to verify the webhook is working"""
    bot = get_bot()
    if not bot:
        return jsonify({'message': 'Bot not initialized'}), 500
    
    try:
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            webhook_info = loop.run_until_complete(bot.get_webhook_info())
            return jsonify({
                'message': 'Webhook info retrieved successfully',
                'webhook_url': webhook_info.url,
                'has_custom_certificate': webhook_info.has_custom_certificate,
                'pending_update_count': webhook_info.pending_update_count,
                'last_error_date': webhook_info.last_error_date,
                'last_error_message': webhook_info.last_error_message,
                'max_connections': webhook_info.max_connections
            }), 200
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"Error getting webhook info: {e}")
        return jsonify({'message': f'Error getting webhook info: {str(e)}'}), 500

# ========== Independent Admin APIs ==========

@telegram_bp.route('/telegram/kick-user', methods=['POST'])
def kick_user():
    """
    Kick a user from a Telegram group.
    Body accepts either:
      - product_id (string) and telegram_user_id (int/string)
      - telegram_group_id (string) and telegram_user_id (int/string)
    """
    try:
        data = request.get_json(force=True) or {}
        product_id = data.get('product_id')
        telegram_group_id = data.get('telegram_group_id')
        telegram_user_id = data.get('telegram_user_id')

        if not telegram_user_id:
            return jsonify({'message': 'telegram_user_id is required'}), 400

        # Resolve chat_id
        chat_id = None
        if product_id:
            product = Product.query.get(product_id)
            if not product or not product.telegram_group:
                return jsonify({'message': 'Product not found or not mapped to a Telegram group'}), 404
            telegram_group_id = product.telegram_group.telegram_group_id
            chat_id = int(str(telegram_group_id))
        elif telegram_group_id:
            chat_id = int(str(telegram_group_id))
        else:
            return jsonify({'message': 'Either product_id or telegram_group_id is required'}), 400

        # Resolve user_id
        try:
            user_id = int(str(telegram_user_id))
        except ValueError:
            return jsonify({'message': 'telegram_user_id must be numeric'}), 400

        success, message = tg_bot.remove_user(chat_id, user_id)
        status = 200 if success else 400
        return jsonify({'success': success, 'message': message}), status
    except Exception as e:
        logger.exception('Error in /telegram/kick-user')
        return jsonify({'message': str(e)}), 500

@telegram_bp.route('/telegram/kick-by-email', methods=['POST'])
def kick_by_email():
    """
    Kick a user from a Telegram group by email + product_id (string).
    Body: { "email": "user@example.com", "product_id": "pro-basic" }
    Looks up the user's telegram_user_id and product's mapped telegram_group_id.
    """
    try:
        data = request.get_json(force=True) or {}
        email = data.get('email')
        product_id = data.get('product_id')
        if not email or not product_id:
            return jsonify({'message': 'email and product_id are required'}), 400

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'message': 'User not found'}), 404
        if not user.telegram_user_id:
            return jsonify({'message': 'User has no linked telegram_user_id'}), 400

        subscription = Subscription.query.filter(
            Subscription.user_id == user.id,
            Subscription.product_id == product_id,
            Subscription.status.in_(["active", "pending_join"]),
        ).first()
        if not subscription:
            return jsonify({'message': 'Active/pending subscription not found for user and product'}), 404

        product = Product.query.get(product_id)
        if not product or not product.telegram_group:
            return jsonify({'message': 'Product not mapped to a Telegram group'}), 404

        chat_id = int(str(product.telegram_group.telegram_group_id))
        user_id = int(str(user.telegram_user_id))

        success, message = tg_bot.remove_user(chat_id, user_id)
        status = 200 if success else 400
        return jsonify({'success': success, 'message': message}), status
    except Exception as e:
        logger.exception('Error in /telegram/kick-by-email')
        return jsonify({'message': str(e)}), 500

@telegram_bp.route('/telegram/invite/regenerate', methods=['POST'])
def regenerate_invite():
    """
    Regenerate an invite link for a Telegram group.
    Body accepts either:
      - product_id (string)
      - telegram_group_id (string)
    Optional:
      - token (string). If omitted, a token will be generated.
    """
    try:
        import uuid
        data = request.get_json(force=True) or {}
        product_id = data.get('product_id')
        telegram_group_id = data.get('telegram_group_id')
        token = data.get('token') or str(uuid.uuid4())[:32]

        # Resolve chat_id
        chat_id = None
        if product_id:
            product = Product.query.get(product_id)
            if not product or not product.telegram_group:
                return jsonify({'message': 'Product not found or not mapped to a Telegram group'}), 404
            telegram_group_id = product.telegram_group.telegram_group_id
            chat_id = int(str(telegram_group_id))
        elif telegram_group_id:
            chat_id = int(str(telegram_group_id))
        else:
            return jsonify({'message': 'Either product_id or telegram_group_id is required'}), 400

        success, msg, invite_link = tg_bot.create_invite_link(chat_id, token)
        status = 200 if success else 400
        return jsonify({'success': success, 'message': msg, 'invite_link': invite_link, 'token': token}), status
    except Exception as e:
        logger.exception('Error in /telegram/invite/regenerate')
        return jsonify({'message': str(e)}), 500