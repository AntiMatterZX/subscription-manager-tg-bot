from datetime import datetime
from app import db


class TelegramGroup(db.Model):
    __tablename__ = "telegram_groups"

    id = db.Column(db.Integer, primary_key=True)
    telegram_group_id = db.Column(db.String(100), unique=True, nullable=False)
    telegram_group_name = db.Column(db.String(255), nullable=False)
    product_id = db.Column(
        db.Integer, db.ForeignKey("products.id"), unique=True, nullable=True
    )
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationship with Product (one-to-one)
    product = db.relationship("Product", back_populates="telegram_group")

    # Relationship with Subscription (one-to-many)
    subscriptions = db.relationship(
        "Subscription", back_populates="telegram_group", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<TelegramGroup {self.telegram_group_name}>"
