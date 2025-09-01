from datetime import datetime, timezone
from app import db


class TelegramGroup(db.Model):
    __tablename__ = "telegram_groups"

    id = db.Column(db.Integer, primary_key=True)
    telegram_group_id = db.Column(db.String(100), unique=True, nullable=False)
    telegram_group_name = db.Column(db.String(255), nullable=False)
    product_id = db.Column(
        db.String(24), db.ForeignKey("products.id"), nullable=True
    )
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationship with Product (many-to-one)
    product = db.relationship("Product", back_populates="telegram_groups")

    # Relationship with Subscription (one-to-many)
    subscriptions = db.relationship(
        "Subscription", back_populates="telegram_group", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<TelegramGroup {self.telegram_group_name}>"
