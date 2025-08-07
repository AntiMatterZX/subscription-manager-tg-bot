from datetime import datetime, timezone
from app import db
import uuid


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationship with TelegramGroup (one-to-one)
    telegram_group = db.relationship(
        "TelegramGroup", uselist=False, back_populates="product"
    )

    # Relationship with Subscription (one-to-many)
    subscriptions = db.relationship(
        "Subscription", back_populates="product", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Product {self.name}>"
