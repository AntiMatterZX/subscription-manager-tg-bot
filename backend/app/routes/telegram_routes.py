import os
import logging
from flask import Blueprint, request, jsonify
from app.bot.telegram_handler import process_update
from app.bot.telegram_client import get_bot

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