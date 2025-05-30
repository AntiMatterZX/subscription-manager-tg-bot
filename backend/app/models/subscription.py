from datetime import datetime
from app import db

class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    telegram_group_id = db.Column(db.Integer, db.ForeignKey('telegram_groups.id'), nullable=False)
    invite_link_token = db.Column(db.String(255), unique=True, nullable=True)
    invite_link_url = db.Column(db.String(512), nullable=True)
    invite_link_expires_at = db.Column(db.DateTime, nullable=True)
    subscription_starts_at = db.Column(db.DateTime, default=datetime.utcnow)
    subscription_expires_at = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending_join')  # pending_join, active, expired, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='subscriptions')
    product = db.relationship('Product', back_populates='subscriptions')
    telegram_group = db.relationship('TelegramGroup', back_populates='subscriptions')
    
    def __repr__(self):
        return f'<Subscription {self.id} - User: {self.user_id}, Product: {self.product_id}>'