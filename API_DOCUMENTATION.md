# Telegram Group Manager API Documentation

This document provides detailed information about the API endpoints available in the Telegram Group Manager application.

## Table of Contents

1. [Product API](#product-api)
2. [Group API](#group-api)
3. [Subscription API](#subscription-api)
4. [Telegram API](#telegram-api)
5. [User API](#user-api)

---

## Product API

The Product API allows you to manage products in the system.

### Get All Products

Retrieves a list of all products.

- **URL**: `/products`
- **Method**: `GET`
- **Authentication**: Not required
- **Response Codes**:
  - `200 OK`: Successfully retrieved products
  
**Response Format**:
```json
{
  "data": [
    {
      "id": "pro-basic",
      "name": "Product Name",
      "description": "Product Description",
      "created_at": "2023-01-01T12:00:00Z",
      "updated_at": "2023-01-01T12:00:00Z"
    }
  ]
}
```

### Get Product by ID

Retrieves a specific product by its ID.

- **URL**: `/products/<product_id>`
- **Method**: `GET`
- **URL Parameters**:
  - `product_id`: String product ID
- **Authentication**: Not required
- **Response Codes**:
  - `200 OK`: Successfully retrieved product
  - `404 Not Found`: Product not found
  
**Response Format**:
```json
{
  "id": "pro-basic",
  "name": "Product Name",
  "description": "Product Description",
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z"
}
```

### Create Product

Creates a new product.

- **URL**: `/products`
- **Method**: `POST`
- **Authentication**: Not required
- **Request Body**:
```json
{
  "id": "pro-basic",
  "name": "New Product",
  "description": "Product Description"
}
```
- **Response Codes**:
  - `201 Created`: Successfully created product
  - `400 Bad Request`: Validation error
  - `500 Internal Server Error`: Server error
  
**Response Format**:
```json
{
  "id": "pro-basic",
  "name": "New Product",
  "description": "Product Description",
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z"
}
```

### Update Product

Updates an existing product.

- **URL**: `/products/<product_id>`
- **Method**: `PUT`
- **URL Parameters**:
  - `product_id`: String product ID
- **Authentication**: Not required
- **Request Body**:
```json
{
  "name": "Updated Product Name",
  "description": "Updated Description"
}
```
- **Response Codes**:
  - `200 OK`: Successfully updated product
  - `400 Bad Request`: Validation error
  - `404 Not Found`: Product not found
  - `500 Internal Server Error`: Server error
  
**Response Format**:
```json
{
  "id": "pro-basic",
  "name": "Updated Product Name",
  "description": "Updated Description",
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-02T12:00:00Z"
}
```

### Delete Product

Deletes a product.

- **URL**: `/products/<product_id>`
- **Method**: `DELETE`
- **URL Parameters**:
  - `product_id`: String product ID
- **Authentication**: Not required
- **Response Codes**:
  - `200 OK`: Successfully deleted product
  - `404 Not Found`: Product not found
  - `500 Internal Server Error`: Server error
  
**Response Format**:
```json
{
  "message": "Product deleted successfully"
}
```

---

## Group API

The Group API allows you to manage Telegram groups and their mappings to products.

### Get All Groups

Retrieves a list of all Telegram groups.

- **URL**: `/groups`
- **Method**: `GET`
- **Authentication**: Not required
- **Response Codes**:
  - `200 OK`: Successfully retrieved groups
  
**Response Format**:
```json
[
  {
    "id": 1,
    "telegram_group_id": "-1001234567890",
    "telegram_group_name": "Group Name",
    "product_id": "pro-basic",
    "created_at": "2023-01-01T12:00:00Z",
    "updated_at": "2023-01-01T12:00:00Z"
  }
]
```

### Get Unmapped Groups

Retrieves a list of Telegram groups that are not mapped to any product.

- **URL**: `/groups/unmapped`
- **Method**: `GET`
- **Authentication**: Not required
- **Response Codes**:
  - `200 OK`: Successfully retrieved unmapped groups
  
**Response Format**:
```json
[
  {
    "id": 1,
    "telegram_group_id": "-1001234567890",
    "telegram_group_name": "Group Name",
    "product_id": null,
    "created_at": "2023-01-01T12:00:00Z",
    "updated_at": "2023-01-01T12:00:00Z"
  }
]
```

### Map Product to Group

Maps a product to a Telegram group.

- **URL**: `/products/<product_id>/map`
- **Method**: `POST`
- **URL Parameters**:
  - `product_id`: String product ID
- **Authentication**: Not required
- **Request Body**:
```json
{
  "telegram_group_id": "-1001234567890",
  "telegram_group_name": "Group Name"
}
```
- **Response Codes**:
  - `200 OK`: Successfully mapped product to group
  - `400 Bad Request`: Missing required fields or other error
  - `500 Internal Server Error`: Server error
  
**Response Format**:
```json
{
  "id": 1,
  "telegram_group_id": "-1001234567890",
  "telegram_group_name": "Group Name",
  "product_id": "pro-basic",
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z"
}
```

### Unmap Product from Group

Removes the mapping between a product and a Telegram group.

- **URL**: `/products/<product_id>/unmap`
- **Method**: `DELETE`
- **URL Parameters**:
  - `product_id`: String product ID
- **Authentication**: Not required
- **Response Codes**:
  - `200 OK`: Successfully unmapped product
  - `404 Not Found`: No mapping found for this product
  - `500 Internal Server Error`: Server error
  
**Response Format**:
```json
{
  "message": "Product unmapped successfully"
}
```

---

## Subscription API

The Subscription API allows you to manage user subscriptions to products.

### Get All Subscriptions

Retrieves a paginated list of all subscriptions with filtering options.

- **URL**: `/subscriptions`
- **Method**: `GET`
- **Query Parameters**:
  - `page`: Page number (default: 1)
  - `per_page`: Items per page (default: 10, max: 100)
  - `sort_by`: Field to sort by (default: "created_at")
  - `sort_order`: Sort direction, "asc" or "desc" (default: "desc")
  - `search`: Search term to filter results
  - `status`: Filter by subscription status
  - `product_id`: Filter by string product ID
  - `user_id`: Filter by user ID (integer)
- **Authentication**: Not required
- **Response Codes**:
  - `200 OK`: Successfully retrieved subscriptions
  
**Response Format**:
```json
{
  "items": [
    {
      "id": 1,
      "user_id": 1,
      "product_id": "pro-basic",
      "status": "active",
      "subscription_expires_at": "2024-01-01T12:00:00Z",
      "invite_link_url": "https://t.me/joinchat/abcdefg",
      "invite_link_expires_at": "2023-02-01T12:00:00Z",
      "created_at": "2023-01-01T12:00:00Z",
      "updated_at": "2023-01-01T12:00:00Z"
    }
  ],
  "total": 50,
  "page": 1,
  "per_page": 10,
  "pages": 5
}
```

### Create Subscription

Creates a new subscription for a user to a product.

- **URL**: `/subscribe`
- **Method**: `POST`
- **Authentication**: Not required
- **Request Body**:
```json
{
  "email": "user@example.com",
  "product_id": "pro-basic",
  "expiration_datetime": "2024-01-01T12:00:00Z"
}
```
OR
```json
{
  "email": "user@example.com",
  "product_name": "Product Name",
  "expiration_datetime": "2024-01-01T12:00:00Z"
}
```
- **Response Codes**:
  - `201 Created`: Successfully created subscription
  - `400 Bad Request`: Validation error
  - `500 Internal Server Error`: Server error
  
**Response Format**:
```json
{
  "message": "Subscription created successfully",
  "invite_link": "https://t.me/joinchat/abcdefg",
  "invite_expires_at": "2023-02-01T12:00:00Z",
  "subscription_expires_at": "2024-01-01T12:00:00Z"
}
```

### Cancel Subscription by Email and Product ID

Cancels a subscription based on user email and product ID.

- **URL**: `/subscriptions`
- **Method**: `DELETE`
- **Authentication**: Not required
- **Request Body**:
```json
{
  "email": "user@example.com",
  "product_id": "pro-basic"
}
```
- **Response Codes**:
  - `200 OK`: Successfully cancelled subscription
  - `400 Bad Request`: Validation error
  - `500 Internal Server Error`: Server error
  
**Response Format**:
```json
{
  "message": "Subscription cancelled successfully"
}
```

### Get All Users

Retrieves a list of all users.

- **URL**: `/users`
- **Method**: `GET`
- **Authentication**: Not required
- **Response Codes**:
  - `200 OK`: Successfully retrieved users
  
**Response Format**:
```json
[
  {
    "id": 1,
    "email": "user@example.com"
  }
]
```

### Cancel Subscription by ID

Cancels a subscription by its ID.

- **URL**: `/subscriptions/<subscription_id>/cancel`
- **Method**: `POST`
- **URL Parameters**:
  - `subscription_id`: The ID of the subscription to cancel
- **Authentication**: Not required
- **Response Codes**:
  - `200 OK`: Successfully cancelled subscription
  - `400 Bad Request`: Error cancelling subscription
  - `500 Internal Server Error`: Server error
  
**Response Format**:
```json
{
  "message": "Subscription cancelled successfully"
}
```

---

## Telegram API

The Telegram API handles webhook interactions with the Telegram Bot API, along with admin operations.

### Telegram Webhook

Endpoint for receiving updates from Telegram.

- **URL**: `/telegram/webhook/<token>`
- **Method**: `POST`
- **URL Parameters**:
  - `token`: The Telegram bot token for verification
- **Authentication**: Token-based (only for this endpoint)
- **Request Body**: Telegram Update object
- **Response Codes**:
  - `200 OK`: Update processed successfully
  - `401 Unauthorized`: Invalid token
  - `500 Internal Server Error`: Error processing update
  
**Response Format**:
```json
{
  "message": "Update processed successfully"
}
```

### Test Webhook

Tests the Telegram webhook configuration.

- **URL**: `/telegram/webhook/test`
- **Method**: `GET`
- **Authentication**: Not required
- **Response Codes**:
  - `200 OK`: Webhook info retrieved successfully
  - `500 Internal Server Error`: Error getting webhook info
  
**Response Format**:
```json
{
  "message": "Webhook info retrieved successfully",
  "webhook_url": "https://example.com/telegram/webhook/token",
  "has_custom_certificate": false,
  "pending_update_count": 0,
  "last_error_date": null,
  "last_error_message": null,
  "max_connections": 40
}
```

### Kick User (Admin)

Kicks a user from a Telegram group by product mapping or direct Telegram group ID.

- **URL**: `/telegram/kick-user`
- **Method**: `POST`
- **Authentication**: Not required
- **Request Body** (one of):
```json
{
  "product_id": "pro-basic",
  "telegram_user_id": 123456789
}
```
OR
```json
{
  "telegram_group_id": "-1001234567890",
  "telegram_user_id": 123456789
}
```
- **Response Codes**:
  - `200 OK`: User removed successfully
  - `400 Bad Request`: Validation error or user not in chat
  - `404 Not Found`: Product not found or not mapped
  - `500 Internal Server Error`: Server error
  
**Response Format**:
```json
{
  "success": true,
  "message": "User 123456789 removed successfully"
}
```

### Regenerate Invite Link (Admin)

Creates a new invite link for a Telegram group by product mapping or direct Telegram group ID.

- **URL**: `/telegram/invite/regenerate`
- **Method**: `POST`
- **Authentication**: Not required
- **Request Body** (one of):
```json
{
  "product_id": "pro-basic",
  "token": "optional-custom-token"
}
```
OR
```json
{
  "telegram_group_id": "-1001234567890",
  "token": "optional-custom-token"
}
```
- **Response Codes**:
  - `200 OK`: Invite link created successfully
  - `400 Bad Request`: Validation error
  - `404 Not Found`: Product not found or not mapped
  - `500 Internal Server Error`: Server error
  
**Response Format**:
```json
{
  "success": true,
  "message": "Invite link created successfully",
  "invite_link": "https://t.me/+abcdefg",
  "token": "generated-or-provided-token"
}
```

---

## User API

### List Users Joined via Invite

Lists users who have joined via an invite link (i.e., users with recorded Telegram IDs), with their related product and group context.

- **URL**: `/users/joined`
- **Method**: `GET`
- **Query Parameters** (optional):
  - `product_id`: Filter by string product ID
  - `telegram_group_id`: Filter by Telegram group ID (string)
  - `status`: Comma-separated subscription statuses (pending_join, active, expired, cancelled)
- **Authentication**: Not required
- **Response Codes**:
  - `200 OK`: Successfully retrieved users
  
**Response Format** (array):
```json
[
  {
    "subscription_id": 101,
    "status": "active",
    "subscription_expires_at": "2024-01-01T12:00:00Z",
    "invite_link_url": "https://t.me/+abcdefg",
    "invite_link_expires_at": "2023-02-01T12:00:00Z",
    "user": {
      "id": 5,
      "email": "user@example.com",
      "telegram_user_id": "123456789",
      "telegram_username": "theuser"
    },
    "product": {
      "id": "pro-basic",
      "name": "Basic",
      "description": "..."
    },
    "telegram_group": {
      "id": 7,
      "telegram_group_id": "-1001234567890",
      "telegram_group_name": "Group Name",
      "is_active": true
    }
  }
]
```

### List Members of a Product

- **URL**: `/products/<product_id>/members`
- **Method**: `GET`
- **URL Parameters**:
  - `product_id`: String product ID
- **Authentication**: Not required

### List Members of a Telegram Group

- **URL**: `/groups/<telegram_group_id>/members`
- **Method**: `GET`
- **URL Parameters**:
  - `telegram_group_id`: Telegram group ID (string)
- **Authentication**: Not required

---

## How Kicking Works and Storage

- When a user joins via invite, the bot extracts the invite token and updates the corresponding subscription with `telegram_user_id` and `telegram_username`.
- Data is stored in PostgreSQL via SQLAlchemy models (`users`, `subscriptions`, `telegram_groups`, `products`).
- Kicking uses `tg_bot.remove_user(chat_id, user_id)` where `chat_id` is the `telegram_group_id` and `user_id` is the `telegram_user_id` from the subscription/user record.
- No MongoDB is required.

---

## Schemas

### Product Schema
- `id`: String - Unique identifier (1-24 chars, provided by client)
- `name`: String - Product name
- `description`: String - Product description
- `created_at`: DateTime - Creation timestamp
- `updated_at`: DateTime - Last update timestamp

### Telegram Group Schema
- `id`: Integer - Unique identifier
- `telegram_group_id`: String - Telegram's internal group ID
- `telegram_group_name`: String - Group name
- `product_id`: String - Associated product ID (nullable)
- `created_at`: DateTime - Creation timestamp
- `updated_at`: DateTime - Last update timestamp

### Subscription Schema
- `id`: Integer - Unique identifier
- `user_id`: Integer - User ID
- `product_id`: String - Product ID
- `status`: String - Subscription status (pending_join, active, expired, cancelled)
- `subscription_expires_at`: DateTime - Expiration timestamp
- `invite_link_url`: String - Telegram group invite link
- `invite_link_expires_at`: DateTime - Invite link expiration timestamp
- `created_at`: DateTime - Creation timestamp
- `updated_at`: DateTime - Last update timestamp

### User Schema
- `id`: Integer - Unique identifier
- `email`: String - User email address
- `telegram_user_id`: String - User Telegram ID (when known)
- `telegram_username`: String - Telegram username (when known)