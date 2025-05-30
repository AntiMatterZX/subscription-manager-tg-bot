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
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API integration
│   │   └── hooks/          # Custom React hooks
│   ├── Dockerfile          # Frontend Dockerfile
│   └── package.json        # Node.js dependencies
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
- `POST /api/products` - Create a new product
- `PUT /api/products/{product_id}` - Update a product
- `DELETE /api/products/{product_id}` - Delete a product

### Groups

- `GET /api/groups` - List all Telegram groups
- `GET /api/groups/unmapped` - List unmapped Telegram groups

### Mapping

- `POST /api/products/{product_id}/map` - Map a product to a Telegram group
- `DELETE /api/products/{product_id}/unmap` - Unmap a product from a Telegram group

### Subscriptions

- `POST /api/subscribe` - Create a new subscription
- `GET /api/subscriptions` - List all subscriptions (admin only)

## License

[MIT](LICENSE)