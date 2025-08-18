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

    # Register original blueprints (for backward compatibility)
    from app.routes.product_routes import product_bp
    from app.routes.group_routes import group_bp
    from app.routes.subscription_routes import subscription_bp
    from app.routes.telegram_routes import telegram_bp
    from app.routes.user_routes import user_bp

    app.register_blueprint(product_bp, url_prefix="/api/v1")
    app.register_blueprint(group_bp, url_prefix="/api/v1")
    app.register_blueprint(subscription_bp, url_prefix="/api/v1")
    app.register_blueprint(telegram_bp, url_prefix="/api/v1")
    app.register_blueprint(user_bp, url_prefix="/api/v1")

    # Initialize Telegram bot
    from app.services.telegram import tg_bot
    tg_bot.init_app(app)
    tg_bot.start_bot()

    # Initialize scheduled tasks
    from app.tasks.subscription_tasks import init_scheduler

    init_scheduler()

    return app
