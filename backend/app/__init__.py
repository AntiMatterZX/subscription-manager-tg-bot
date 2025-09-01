from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize SQLAlchemy
db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)

    import os

    # Configure the app
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL",
        f"postgresql://{os.environ.get('POSTGRES_USER', 'postgres')}:"
        f"{os.environ.get('POSTGRES_PASSWORD', 'postgres')}@"
        f"{os.environ.get('POSTGRES_HOST', 'db')}:5432/"
        f"{os.environ.get('POSTGRES_DB', 'tg_manager')}",
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # Initialize Swagger API
    from app.swagger_config import api
    api.init_app(app)

    # Register Swagger namespaces
    from app.swagger_routes import products_ns, groups_ns, subscriptions_ns, users_ns, telegram_ns, subscribe_ns
    api.add_namespace(products_ns)
    api.add_namespace(groups_ns)
    api.add_namespace(subscriptions_ns)
    api.add_namespace(users_ns)
    api.add_namespace(telegram_ns)
    api.add_namespace(subscribe_ns)

    # Add redirect route for /api-docs
    @app.route('/api-docs')
    def api_docs():
        from flask import redirect
        return redirect('/api-docs/')
    
    # Add health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'message': 'Application is running'}, 200

    # Legacy routes removed - using Swagger API only

    # Initialize Telegram bot (only if token is provided)
    telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if telegram_token:
        from app.services.telegram import tg_bot
        tg_bot.init_app(app)
        tg_bot.start_bot()
    else:
        print("Warning: TELEGRAM_BOT_TOKEN not set. Telegram bot will not start.")

    # Initialize scheduled tasks
    try:
        from app.tasks.subscription_tasks import init_scheduler
        init_scheduler()
    except Exception as e:
        print(f"Warning: Failed to initialize scheduler: {e}")

    return app
