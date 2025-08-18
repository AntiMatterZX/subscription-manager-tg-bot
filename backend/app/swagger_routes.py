from flask import request, jsonify
from flask_restx import Resource, Namespace
from marshmallow import ValidationError
from app.services import ProductService, TelegramGroupService, SubscriptionService
from app.schemas import (
    product_schema, products_schema, product_create_schema, product_update_schema,
    telegram_group_schema, telegram_groups_schema,
    subscription_schema, subscriptions_schema, subscription_request_schema
)
from app.swagger_config import (
    product_model, product_create_model, product_update_model, error_model, validation_error_model,
    telegram_group_model, group_mapping_model, success_message_model,
    subscription_model, subscription_request_model, subscription_response_model, paginated_subscriptions_model,
    user_model, member_model, kick_user_model, kick_by_email_model, regenerate_invite_model, telegram_response_model,
    regenerate_user_invite_model, invite_link_response_model
)
from app.models import User, Subscription, Product, TelegramGroup
from app.services.telegram import tg_bot
from sqlalchemy import and_
import logging

logger = logging.getLogger(__name__)

# Product namespace
products_ns = Namespace('products', description='Product management operations')

@products_ns.route('')
class ProductList(Resource):
    @products_ns.doc('list_products')
    @products_ns.marshal_list_with(product_model)
    def get(self):
        """Get all products"""
        products = ProductService.get_all_products()
        return products_schema.dump(products)

    @products_ns.doc('create_product')
    @products_ns.expect(product_create_model)
    @products_ns.marshal_with(product_model, code=201)
    @products_ns.response(400, 'Validation error', validation_error_model)
    @products_ns.response(500, 'Internal server error', error_model)
    def post(self):
        """Create a new product"""
        try:
            product_data = product_create_schema.load(request.json)
            product = ProductService.create_product(product_data)
            return product_schema.dump(product), 201
        except ValidationError as e:
            return {'message': 'Validation error', 'errors': e.messages}, 400
        except Exception as e:
            return {'message': str(e)}, 500

@products_ns.route('/<string:product_id>')
@products_ns.param('product_id', 'Product ID (string)')
class Product(Resource):
    @products_ns.doc('get_product')
    @products_ns.marshal_with(product_model)
    @products_ns.response(404, 'Product not found', error_model)
    def get(self, product_id):
        """Get a specific product"""
        product = ProductService.get_product_by_id(product_id)
        if not product:
            return {'message': 'Product not found'}, 404
        return product_schema.dump(product)

    @products_ns.doc('update_product')
    @products_ns.expect(product_update_model)
    @products_ns.marshal_with(product_model)
    @products_ns.response(400, 'Validation error', validation_error_model)
    @products_ns.response(404, 'Product not found', error_model)
    @products_ns.response(500, 'Internal server error', error_model)
    def put(self, product_id):
        """Update a product"""
        try:
            product_data = product_update_schema.load(request.json)
            product = ProductService.update_product(product_id, product_data)
            if not product:
                return {'message': 'Product not found'}, 404
            return product_schema.dump(product)
        except ValidationError as e:
            return {'message': 'Validation error', 'errors': e.messages}, 400
        except Exception as e:
            return {'message': str(e)}, 500

    @products_ns.doc('delete_product')
    @products_ns.marshal_with(success_message_model)
    @products_ns.response(404, 'Product not found', error_model)
    @products_ns.response(500, 'Internal server error', error_model)
    def delete(self, product_id):
        """Delete a product"""
        try:
            success = ProductService.delete_product(product_id)
            if not success:
                return {'message': 'Product not found'}, 404
            return {'message': 'Product deleted successfully'}
        except Exception as e:
            return {'message': str(e)}, 500

@products_ns.route('/<string:product_id>/map')
@products_ns.param('product_id', 'Product ID (string)')
class ProductMapping(Resource):
    @products_ns.doc('map_product_to_group')
    @products_ns.expect(group_mapping_model)
    @products_ns.marshal_with(telegram_group_model)
    @products_ns.response(400, 'Bad request', error_model)
    @products_ns.response(500, 'Internal server error', error_model)
    def post(self, product_id):
        """Map a product to a Telegram group"""
        try:
            data = request.json
            if not data or 'telegram_group_id' not in data or 'telegram_group_name' not in data:
                return {'message': 'Missing required fields: telegram_group_id and telegram_group_name'}, 400
            
            group, error = TelegramGroupService.map_product_to_group(
                product_id, 
                data['telegram_group_id'], 
                data['telegram_group_name']
            )
            
            if error:
                return {'message': error}, 400
            
            return telegram_group_schema.dump(group)
        except Exception as e:
            return {'message': str(e)}, 500

@products_ns.route('/<string:product_id>/unmap')
@products_ns.param('product_id', 'Product ID (string)')
class ProductUnmapping(Resource):
    @products_ns.doc('unmap_product')
    @products_ns.marshal_with(success_message_model)
    @products_ns.response(404, 'No mapping found', error_model)
    @products_ns.response(500, 'Internal server error', error_model)
    def delete(self, product_id):
        """Unmap a product from a Telegram group"""
        try:
            success = TelegramGroupService.unmap_product(product_id)
            if not success:
                return {'message': 'No mapping found for this product'}, 404
            return {'message': 'Product unmapped successfully'}
        except Exception as e:
            return {'message': str(e)}, 500

@products_ns.route('/<string:product_id>/members')
@products_ns.param('product_id', 'Product ID (string)')
class ProductMembers(Resource):
    @products_ns.doc('list_product_members')
    @products_ns.marshal_list_with(member_model)
    def get(self, product_id):
        """List members for a product"""
        def _serialize_member(sub):
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
        
        q = (
            Subscription.query.join(User).join(Product).outerjoin(TelegramGroup)
            .filter(Subscription.product_id == product_id)
            .filter(User.telegram_user_id.isnot(None))
        )
        subs = q.all()
        return [_serialize_member(s) for s in subs]

# Groups namespace
groups_ns = Namespace('groups', description='Telegram group operations')

@groups_ns.route('')
class GroupList(Resource):
    @groups_ns.doc('list_groups')
    @groups_ns.marshal_list_with(telegram_group_model)
    def get(self):
        """Get all Telegram groups"""
        groups = TelegramGroupService.get_all_groups()
        return telegram_groups_schema.dump(groups)

@groups_ns.route('/unmapped')
class UnmappedGroups(Resource):
    @groups_ns.doc('list_unmapped_groups')
    @groups_ns.marshal_list_with(telegram_group_model)
    def get(self):
        """Get unmapped Telegram groups"""
        groups = TelegramGroupService.get_unmapped_groups()
        return telegram_groups_schema.dump(groups)

@groups_ns.route('/<string:telegram_group_id>/members')
@groups_ns.param('telegram_group_id', 'Telegram group ID')
class GroupMembers(Resource):
    @groups_ns.doc('list_group_members')
    @groups_ns.marshal_list_with(member_model)
    def get(self, telegram_group_id):
        """List members for a Telegram group"""
        def _serialize_member(sub):
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
        
        q = (
            Subscription.query.join(User).join(Product).outerjoin(TelegramGroup)
            .filter(TelegramGroup.telegram_group_id == str(telegram_group_id))
            .filter(User.telegram_user_id.isnot(None))
        )
        subs = q.all()
        return [_serialize_member(s) for s in subs]

# Subscriptions namespace
subscriptions_ns = Namespace('subscriptions', description='Subscription management')

@subscriptions_ns.route('')
class SubscriptionList(Resource):
    @subscriptions_ns.doc('list_subscriptions')
    @subscriptions_ns.marshal_with(paginated_subscriptions_model)
    @subscriptions_ns.param('page', 'Page number', type='integer', default=1)
    @subscriptions_ns.param('per_page', 'Items per page', type='integer', default=10)
    @subscriptions_ns.param('sort_by', 'Sort field', default='created_at')
    @subscriptions_ns.param('sort_order', 'Sort order', default='desc')
    @subscriptions_ns.param('search', 'Search term')
    @subscriptions_ns.param('status', 'Filter by status')
    @subscriptions_ns.param('product_id', 'Filter by product ID')
    @subscriptions_ns.param('user_id', 'Filter by user ID', type='integer')
    def get(self):
        """Get all subscriptions (admin only)"""
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        sort_by = request.args.get("sort_by", "created_at")
        sort_order = request.args.get("sort_order", "desc")
        search = request.args.get("search")
        status = request.args.get("status")
        product_id = request.args.get("product_id")
        user_id = request.args.get("user_id", type=int)
        
        per_page = min(per_page, 100)
        
        result = SubscriptionService.get_all_subscriptions(
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            search=search,
            status=status,
            product_id=product_id,
            user_id=user_id
        )
        
        return {
            "items": subscriptions_schema.dump(result["items"]),
            "total": result["total"],
            "page": result["page"],
            "per_page": result["per_page"],
            "pages": result["pages"]
        }

    @subscriptions_ns.doc('cancel_subscription_by_email')
    @subscriptions_ns.expect(subscription_request_model)
    @subscriptions_ns.marshal_with(success_message_model)
    @subscriptions_ns.response(400, 'Bad request', error_model)
    @subscriptions_ns.response(500, 'Internal server error', error_model)
    def delete(self):
        """Cancel subscription by email and product ID"""
        try:
            data = subscription_request_schema.load(request.json)
            subscription, error = (
                SubscriptionService.cancel_subscription_by_email_and_product_id(
                    data["email"], data["product_id"]
                )
            )

            if error:
                return {"message": error}, 400

            return {"message": "Subscription cancelled successfully"}
        except ValidationError as e:
            return {"message": "Validation error", "errors": e.messages}, 400
        except Exception as e:
            logging.exception("Error cancelling subscription")
            return {"message": str(e)}, 500

@subscriptions_ns.route('/<int:subscription_id>/cancel')
@subscriptions_ns.param('subscription_id', 'Subscription ID')
class SubscriptionCancel(Resource):
    @subscriptions_ns.doc('cancel_subscription')
    @subscriptions_ns.marshal_with(success_message_model)
    @subscriptions_ns.response(400, 'Bad request', error_model)
    @subscriptions_ns.response(500, 'Internal server error', error_model)
    def post(self, subscription_id):
        """Cancel a specific subscription"""
        try:
            subscription, error = SubscriptionService.cancel_subscription(subscription_id)

            if error:
                return {"message": error}, 400

            return {"message": "Subscription cancelled successfully"}
        except ValidationError as e:
            return {"message": "Validation error", "errors": e.messages}, 400
        except Exception as e:
            logging.exception("Error cancelling subscription")
            return {"message": str(e)}, 500

# Subscribe namespace (separate for public access)
subscribe_ns = Namespace('subscribe', description='Public subscription creation')

@subscribe_ns.route('')
class Subscribe(Resource):
    @subscribe_ns.doc('create_subscription')
    @subscribe_ns.expect(subscription_request_model)
    @subscribe_ns.marshal_with(subscription_response_model, code=201)
    @subscribe_ns.response(400, 'Bad request', error_model)
    @subscribe_ns.response(500, 'Internal server error', error_model)
    def post(self):
        """Create a new subscription"""
        try:
            data = subscription_request_schema.load(request.json)
            expiration_datetime = data.get("expiration_datetime")

            if data.get("product_id"):
                subscription, error = SubscriptionService.create_subscription(
                    data["email"], data["product_id"], expiration_datetime
                )
            else:
                subscription, error = (
                    SubscriptionService.create_subsciption_by_product_name(
                        data["email"], data["product_name"], expiration_datetime
                    )
                )

            if error:
                return {"message": error}, 400

            result = {
                "message": "Subscription created successfully",
                "invite_link": subscription.invite_link_url,
                "invite_expires_at": subscription.invite_link_expires_at,
                "subscription_expires_at": subscription.subscription_expires_at,
            }

            return result, 201
        except ValidationError as e:
            return {"message": "Validation error", "errors": e.messages}, 400
        except Exception as e:
            logging.exception("Error creating subscription")
            return {"message": str(e)}, 500

# Users namespace
users_ns = Namespace('users', description='User management')

@users_ns.route('')
class UserList(Resource):
    @users_ns.doc('list_users')
    @users_ns.marshal_list_with(user_model)
    def get(self):
        """Get all users"""
        users = User.query.all()
        result = []
        for user in users:
            result.append({
                "id": user.id,
                "email": user.email
            })
        return result

@users_ns.route('/joined')
class JoinedUsers(Resource):
    @users_ns.doc('list_joined_users')
    @users_ns.marshal_list_with(member_model)
    @users_ns.param('product_id', 'Filter by product ID')
    @users_ns.param('telegram_group_id', 'Filter by Telegram group ID')
    @users_ns.param('status', 'Filter by status (comma-separated)')
    def get(self):
        """List users who joined via invite link with context"""
        def _serialize_member(sub):
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
        
        product_id = request.args.get('product_id')
        telegram_group_id = request.args.get('telegram_group_id')
        status_param = request.args.get('status')

        q = Subscription.query.join(User).join(Product).outerjoin(TelegramGroup)
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
        return [_serialize_member(s) for s in subs]

# Telegram namespace
telegram_ns = Namespace('telegram', description='Telegram bot operations')

@telegram_ns.route('/kick-user')
class KickUser(Resource):
    @telegram_ns.doc('kick_user')
    @telegram_ns.expect(kick_user_model)
    @telegram_ns.marshal_with(telegram_response_model)
    @telegram_ns.response(400, 'Bad request', error_model)
    @telegram_ns.response(404, 'Not found', error_model)
    @telegram_ns.response(500, 'Internal server error', error_model)
    def post(self):
        """Kick a user from a Telegram group"""
        try:
            data = request.get_json(force=True) or {}
            product_id = data.get('product_id')
            telegram_group_id = data.get('telegram_group_id')
            telegram_user_id = data.get('telegram_user_id')

            if not telegram_user_id:
                return {'message': 'telegram_user_id is required'}, 400

            chat_id = None
            if product_id:
                product = Product.query.get(product_id)
                if not product or not product.telegram_group:
                    return {'message': 'Product not found or not mapped to a Telegram group'}, 404
                telegram_group_id = product.telegram_group.telegram_group_id
                chat_id = int(str(telegram_group_id))
            elif telegram_group_id:
                chat_id = int(str(telegram_group_id))
            else:
                return {'message': 'Either product_id or telegram_group_id is required'}, 400

            try:
                user_id = int(str(telegram_user_id))
            except ValueError:
                return {'message': 'telegram_user_id must be numeric'}, 400

            success, message = tg_bot.remove_user(chat_id, user_id)
            status = 200 if success else 400
            return {'success': success, 'message': message}, status
        except Exception as e:
            logger.exception('Error in /telegram/kick-user')
            return {'message': str(e)}, 500

@telegram_ns.route('/kick-by-email')
class KickByEmail(Resource):
    @telegram_ns.doc('kick_by_email')
    @telegram_ns.expect(kick_by_email_model)
    @telegram_ns.marshal_with(telegram_response_model)
    @telegram_ns.response(400, 'Bad request', error_model)
    @telegram_ns.response(404, 'Not found', error_model)
    @telegram_ns.response(500, 'Internal server error', error_model)
    def post(self):
        """Kick a user from a Telegram group by email"""
        try:
            data = request.get_json(force=True) or {}
            email = data.get('email')
            product_id = data.get('product_id')
            if not email or not product_id:
                return {'message': 'email and product_id are required'}, 400

            user = User.query.filter_by(email=email).first()
            if not user:
                return {'message': 'User not found'}, 404
            if not user.telegram_user_id:
                return {'message': 'User has no linked telegram_user_id'}, 400

            subscription = Subscription.query.filter(
                Subscription.user_id == user.id,
                Subscription.product_id == product_id,
                Subscription.status.in_(["active", "pending_join"]),
            ).first()
            if not subscription:
                return {'message': 'Active/pending subscription not found for user and product'}, 404

            product = Product.query.get(product_id)
            if not product or not product.telegram_group:
                return {'message': 'Product not mapped to a Telegram group'}, 404

            chat_id = int(str(product.telegram_group.telegram_group_id))
            user_id = int(str(user.telegram_user_id))

            success, message = tg_bot.remove_user(chat_id, user_id)
            status = 200 if success else 400
            return {'success': success, 'message': message}, status
        except Exception as e:
            logger.exception('Error in /telegram/kick-by-email')
            return {'message': str(e)}, 500

@telegram_ns.route('/invite/regenerate')
class RegenerateInvite(Resource):
    @telegram_ns.doc('regenerate_invite')
    @telegram_ns.expect(regenerate_invite_model)
    @telegram_ns.marshal_with(telegram_response_model)
    @telegram_ns.response(400, 'Bad request', error_model)
    @telegram_ns.response(404, 'Not found', error_model)
    @telegram_ns.response(500, 'Internal server error', error_model)
    def post(self):
        """Regenerate an invite link for a Telegram group"""
        try:
            import uuid
            data = request.get_json(force=True) or {}
            product_id = data.get('product_id')
            telegram_group_id = data.get('telegram_group_id')
            token = data.get('token') or str(uuid.uuid4())[:32]

            chat_id = None
            if product_id:
                product = Product.query.get(product_id)
                if not product or not product.telegram_group:
                    return {'message': 'Product not found or not mapped to a Telegram group'}, 404
                telegram_group_id = product.telegram_group.telegram_group_id
                chat_id = int(str(telegram_group_id))
            elif telegram_group_id:
                chat_id = int(str(telegram_group_id))
            else:
                return {'message': 'Either product_id or telegram_group_id is required'}, 400

            success, msg, invite_link = tg_bot.create_invite_link(chat_id, token)
            status = 200 if success else 400
            return {'success': success, 'message': msg, 'invite_link': invite_link, 'token': token}, status
        except Exception as e:
            logger.exception('Error in /telegram/invite/regenerate')
            return {'message': str(e)}, 500

@telegram_ns.route('/webhook/<string:token>')
@telegram_ns.param('token', 'Telegram bot token')
class TelegramWebhook(Resource):
    @telegram_ns.doc('telegram_webhook')
    @telegram_ns.response(200, 'Update processed')
    @telegram_ns.response(401, 'Invalid token')
    def post(self, token):
        """Telegram webhook endpoint"""
        import os
        from app.bot.telegram_handler import process_update
        
        if token != os.environ.get('TELEGRAM_BOT_TOKEN'):
            logger.warning(f"Invalid token received in webhook: {token}")
            return {'message': 'Invalid token'}, 401
        
        try:
            update = request.json
            logger.info(f"Received Telegram update: {update}")
            process_update(update)
            return {'message': 'Update processed successfully'}
        except Exception as e:
            logger.error(f"Error processing Telegram update: {e}")
            return {'message': f'Error processing update: {str(e)}'}, 500

@telegram_ns.route('/webhook/test')
class TelegramWebhookTest(Resource):
    @telegram_ns.doc('test_webhook')
    @telegram_ns.response(200, 'Webhook info retrieved')
    @telegram_ns.response(500, 'Bot not initialized')
    def get(self):
        """Test webhook endpoint"""
        from app.bot.telegram_client import get_bot
        
        bot = get_bot()
        if not bot:
            return {'message': 'Bot not initialized'}, 500
        
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                webhook_info = loop.run_until_complete(bot.get_webhook_info())
                return {
                    'message': 'Webhook info retrieved successfully',
                    'webhook_url': webhook_info.url,
                    'has_custom_certificate': webhook_info.has_custom_certificate,
                    'pending_update_count': webhook_info.pending_update_count,
                    'last_error_date': webhook_info.last_error_date,
                    'last_error_message': webhook_info.last_error_message,
                    'max_connections': webhook_info.max_connections
                }
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Error getting webhook info: {e}")
            return {'message': f'Error getting webhook info: {str(e)}'}, 500

@subscriptions_ns.route('/regenerate-invite')
class RegenerateInviteLink(Resource):
    @subscriptions_ns.doc('regenerate_invite_link')
    @subscriptions_ns.expect(regenerate_user_invite_model)
    @subscriptions_ns.marshal_with(invite_link_response_model)
    @subscriptions_ns.response(400, 'Bad request', error_model)
    @subscriptions_ns.response(404, 'Not found', error_model)
    @subscriptions_ns.response(500, 'Internal server error', error_model)
    def post(self):
        """Regenerate invite link for a subscription"""
        try:
            data = request.get_json(force=True) or {}
            subscription_id = data.get('subscription_id')
            product_id = data.get('product_id')
            user_email = data.get('user_email')
            custom_token = data.get('token')

            if subscription_id:
                subscription, error = SubscriptionService.regenerate_invite_link(
                    subscription_id, custom_token
                )
            elif product_id and user_email:
                subscription, error = SubscriptionService.regenerate_invite_link_by_product(
                    product_id, user_email, custom_token
                )
            else:
                return {'message': 'Either subscription_id or (product_id + user_email) is required'}, 400

            if error:
                return {'message': error}, 400

            return {
                'success': True,
                'message': 'Invite link regenerated successfully',
                'invite_link': subscription.invite_link_url,
                'token': subscription.invite_link_token,
                'subscription_id': subscription.id,
                'expires_at': subscription.invite_link_expires_at
            }
        except Exception as e:
            logging.exception('Error regenerating invite link')
            return {'message': str(e)}, 500

# Export all namespaces
__all__ = ['products_ns', 'groups_ns', 'subscriptions_ns', 'users_ns', 'telegram_ns', 'subscribe_ns']