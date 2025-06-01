from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from bcrypt import hashpw, checkpw, gensalt

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(100), unique=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String(255))
    verification_sent_at = Column(DateTime)
    subscription_tier = Column(String(20), default='free')
    subscription_expires_at = Column(DateTime)
    
    # Profile fields for future use
    first_name = Column(String(100))
    last_name = Column(String(100))
    display_name = Column(String(100))
    avatar_url = Column(String(500))
    bio = Column(Text)
    timezone = Column(String(50), default='UTC')
    locale = Column(String(10), default='en')
    
    # Privacy and sharing
    is_public = Column(Boolean, default=False)
    share_token = Column(String(255), unique=True)  # For therapist sharing
    
    # Notification preferences (denormalized for performance)
    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=False)
    
    # Feature flags
    beta_features = Column(Boolean, default=False)
    
    # Security
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(255))
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)
    
    # Relationships
    entries = db.relationship('JournalEntry', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    preferences = db.relationship('UserPreferences', backref='user', uselist=False, cascade='all, delete-orphan')
    usage_tracking = db.relationship('UsageTracking', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Check if the provided password matches the hash"""
        return checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def get_display_name(self):
        """Get the user's display name with fallbacks"""
        return self.display_name or self.username or self.email.split('@')[0]
    
    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'display_name': self.get_display_name(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'subscription_tier': self.subscription_tier,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'avatar_url': self.avatar_url,
            'timezone': self.timezone,
            'locale': self.locale
        }
    
    def __repr__(self):
        return f'<User {self.username or self.email}>'