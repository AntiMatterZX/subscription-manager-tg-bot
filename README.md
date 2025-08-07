# Advanced Product Subscription and Telegram Group Management System

A full-stack application that allows administrators to manage products and map them to exclusive Telegram groups. Users can subscribe to products and receive time-limited, single-use invite links to join the corresponding Telegram groups.

## Features

- Product management (CRUD operations)
- Telegram group mapping to products (one-to-one)
- User subscription system
- Automatic user identification upon joining Telegram groups
- Automatic removal of users when subscriptions expire

## Tech Stack

- **Backend**: Flask, SQLAlchemy, Marshmallow, Python Telegram Bot
- **Frontend**: React, Vite, Tailwind CSS
- **Database**: PostgreSQL
- **Deployment**: Docker, Docker Compose

## Project Structure

```
tg-manager/
├── backend/                # Flask application
│   ├── app/
│   │   ├── models/         # SQLAlchemy models
│   │   ├── routes/         # API endpoints
│   │   ├── schemas/        # Marshmallow schemas
│   │   ├── services/       # Business logic
│   │   ├── tasks/          # Scheduled tasks
│   │   └── bot/            # Telegram bot logic
│   ├── Dockerfile          # Backend Dockerfile
│   └── requirements.txt    # Python dependencies
├── frontend/               # React application
├── docker-compose.yml      # Docker Compose configuration
└── README.md               # Project documentation
```

## Setup Instructions

### Prerequisites

- Docker and Docker Compose
- Telegram Bot Token (for development and production)

### Environment Variables

Create a `.env` file in the project root with the following variables:

```
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=tg_manager

# Flask
FLASK_APP=app
FLASK_ENV=development
SECRET_KEY=your_secret_key

# Telegram
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```

### Running the Application

1. Clone the repository
2. Create the `.env` file with the required environment variables
3. Run `docker-compose up --build`
4. Access the application at http://localhost:3000

## API Documentation

### Products

- `GET /api/products` - List all products
- `GET /api/products/{product_id}` - Get a specific product
- `POST /api/products` - Create a new product (ID is required and must be a string you provide)
- `PUT /api/products/{product_id}` - Update a product (do not include ID in the body)
- `DELETE /api/products/{product_id}` - Delete a product

Notes:
- Product IDs are strings (1-24 chars) provided by the client.

### Groups

- `GET /api/groups` - List all Telegram groups
- `GET /api/groups/unmapped` - List unmapped Telegram groups

### Mapping

- `POST /api/products/{product_id}/map` - Map a product to a Telegram group
- `DELETE /api/products/{product_id}/unmap` - Unmap a product from a Telegram group

Notes:
- `{product_id}` in mapping routes is a string matching the product's ID.

### Subscriptions

- `POST /api/subscribe` - Create a new subscription
- `GET /api/subscriptions` - List all subscriptions (admin only)

### Telegram

- `POST /api/telegram/kick-user` — Kick a user from a Telegram group
  - Body (one of):
    - `{ "product_id": "string", "telegram_user_id": 123456789 }`
    - `{ "telegram_group_id": "-1001234567890", "telegram_user_id": 123456789 }`
  - Response: `{ success: boolean, message: string }`

- `POST /api/telegram/invite/regenerate` — Regenerate an invite link for a Telegram group
  - Body (one of):
    - `{ "product_id": "string" }`
    - `{ "telegram_group_id": "-1001234567890" }`
  - Optional: `{ "token": "custom-token" }` (if omitted, server generates one)
  - Response: `{ success: boolean, message: string, invite_link: string|null, token: string }`

### Users

- `GET /api/users/joined` — List users who joined via invite link with context
  - Query params (optional): `product_id`, `telegram_group_id`, `status`
  - Returns user, product, group, and subscription details required for admin actions

- `GET /api/products/{product_id}/members` — Convenience list of members for a product (string product_id)
- `GET /api/groups/{telegram_group_id}/members` — Convenience list of members for a Telegram group

Notes:
- The system uses PostgreSQL only; no MongoDB is required. The bot records `telegram_user_id` on the `users` table via subscription updates when a user joins via a tracked invite.

## License

[MIT](LICENSE)