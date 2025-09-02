from flask_restx import Api, Resource, fields, Namespace

# Initialize API with Swagger documentation
api = Api(
    version='1.0',
    title='Subscription Manager API',
    description='API for managing products, subscriptions, and Telegram groups',
    doc='/api-docs/',
    prefix='/api',
    # Use local Swagger UI files to avoid CDN issues
    validate=False
)

# Define common models
error_model = api.model('Error', {
    'message': fields.String(required=True, description='Error message')
})

validation_error_model = api.model('ValidationError', {
    'message': fields.String(required=True, description='Error message'),
    'errors': fields.Raw(description='Validation errors')
})

# Product models
product_model = api.model('Product', {
    'id': fields.String(required=True, description='Product ID (1-24 characters)'),
    'name': fields.String(required=True, description='Product name'),
    'description': fields.String(description='Product description')
})

product_create_model = api.model('ProductCreate', {
    'id': fields.String(required=True, description='Product ID (1-24 characters)'),
    'name': fields.String(required=True, description='Product name'),
    'description': fields.String(description='Product description')
})

product_update_model = api.model('ProductUpdate', {
    'name': fields.String(description='Product name'),
    'description': fields.String(description='Product description')
})

# Group models
telegram_group_model = api.model('TelegramGroup', {
    'id': fields.Integer(description='Internal group ID'),
    'telegram_group_id': fields.String(required=True, description='Telegram group ID'),
    'telegram_group_name': fields.String(required=True, description='Telegram group name'),
    'product_id': fields.String(description='Mapped product ID'),
    'is_active': fields.Boolean(description='Whether group is active')
})

# Add telegram_groups to product model after telegram_group_model is defined
product_model['telegram_groups'] = fields.List(fields.Nested(telegram_group_model), description='Mapped Telegram groups')

group_mapping_model = api.model('GroupMapping', {
    'telegram_group_id': fields.String(required=True, description='Telegram group ID'),
    'telegram_group_name': fields.String(required=True, description='Telegram group name')
})

group_unmap_model = api.model('GroupUnmap', {
    'telegram_group_id': fields.String(description='Telegram group ID (optional - if not provided, unmaps all groups)')
})

# Subscription models
subscription_model = api.model('Subscription', {
    'id': fields.Integer(description='Subscription ID'),
    'user_id': fields.Integer(description='User ID'),
    'product_id': fields.String(description='Product ID'),
    'status': fields.String(description='Subscription status'),
    'subscription_expires_at': fields.DateTime(description='Subscription expiration'),
    'invite_link_url': fields.String(description='Invite link URL'),
    'invite_link_expires_at': fields.DateTime(description='Invite link expiration'),
    'created_at': fields.DateTime(description='Creation timestamp')
})

subscription_request_model = api.model('SubscriptionRequest', {
    'email': fields.String(required=True, description='User email'),
    'product_id': fields.String(description='Product ID'),
    'product_name': fields.String(description='Product name (alternative to product_id)'),
    'expiration_datetime': fields.DateTime(description='Custom expiration datetime')
})

subscription_response_model = api.model('SubscriptionResponse', {
    'message': fields.String(description='Success message'),
    'invite_link': fields.String(description='Telegram invite link'),
    'invite_expires_at': fields.DateTime(description='Invite link expiration'),
    'subscription_expires_at': fields.DateTime(description='Subscription expiration')
})

paginated_subscriptions_model = api.model('PaginatedSubscriptions', {
    'items': fields.List(fields.Nested(subscription_model)),
    'total': fields.Integer(description='Total number of items'),
    'page': fields.Integer(description='Current page'),
    'per_page': fields.Integer(description='Items per page'),
    'pages': fields.Integer(description='Total pages')
})

# User models
user_model = api.model('User', {
    'id': fields.Integer(description='User ID'),
    'email': fields.String(description='User email'),
    'telegram_user_id': fields.String(description='Telegram user ID'),
    'telegram_username': fields.String(description='Telegram username')
})

member_model = api.model('Member', {
    'subscription_id': fields.Integer(description='Subscription ID'),
    'status': fields.String(description='Subscription status'),
    'subscription_expires_at': fields.DateTime(description='Subscription expiration'),
    'invite_link_url': fields.String(description='Invite link URL'),
    'invite_link_expires_at': fields.DateTime(description='Invite link expiration'),
    'user': fields.Nested(user_model),
    'product': fields.Nested(product_model),
    'telegram_group': fields.Nested(telegram_group_model)
})

# Telegram models
kick_user_model = api.model('KickUser', {
    'product_id': fields.String(description='Product ID (alternative to telegram_group_id)'),
    'telegram_group_id': fields.String(description='Telegram group ID (alternative to product_id)'),
    'telegram_user_id': fields.String(required=True, description='Telegram user ID to kick')
})

kick_by_email_model = api.model('KickByEmail', {
    'email': fields.String(required=True, description='User email'),
    'product_id': fields.String(required=True, description='Product ID')
})

regenerate_invite_model = api.model('RegenerateInvite', {
    'product_id': fields.String(description='Product ID (alternative to telegram_group_id)'),
    'telegram_group_id': fields.String(description='Telegram group ID (alternative to product_id)'),
    'token': fields.String(description='Custom token (optional)')
})

regenerate_user_invite_model = api.model('RegenerateUserInvite', {
    'subscription_id': fields.Integer(description='Subscription ID'),
    'product_id': fields.String(description='Product ID (alternative to subscription_id)'),
    'user_email': fields.String(description='User email (required with product_id)'),
    'token': fields.String(description='Custom token (optional)')
})

invite_link_response_model = api.model('InviteLinkResponse', {
    'success': fields.Boolean(description='Operation success'),
    'message': fields.String(description='Response message'),
    'invite_link': fields.String(description='Generated invite link'),
    'token': fields.String(description='Token used'),
    'subscription_id': fields.Integer(description='Subscription ID'),
    'expires_at': fields.DateTime(description='Link expiration time')
})

telegram_response_model = api.model('TelegramResponse', {
    'success': fields.Boolean(description='Operation success'),
    'message': fields.String(description='Response message'),
    'invite_link': fields.String(description='Generated invite link (for regenerate)'),
    'token': fields.String(description='Token used (for regenerate)')
})

success_message_model = api.model('SuccessMessage', {
    'message': fields.String(description='Success message')
})