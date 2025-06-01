from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from app.models.user import db

class UsageTracking(db.Model):
    __tablename__ = 'usage_tracking'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    entry_count = Column(Integer, default=0)
    month_year = Column(String(7))  # Format: "2024-01"
    last_entry_at = Column(DateTime)
    
    # Ensure one record per user per month
    __table_args__ = (
        UniqueConstraint('user_id', 'month_year', name='_user_month_uc'),
    )
    
    @classmethod
    def get_or_create_current_month(cls, user_id):
        """Get or create usage tracking for current month"""
        current_month = datetime.utcnow().strftime('%Y-%m')
        
        tracking = cls.query.filter_by(
            user_id=user_id,
            month_year=current_month
        ).first()
        
        if not tracking:
            tracking = cls(
                user_id=user_id,
                month_year=current_month,
                entry_count=0
            )
            db.session.add(tracking)
            db.session.commit()
        
        return tracking
    
    def increment_usage(self):
        """Increment entry count and update last entry timestamp"""
        self.entry_count += 1
        self.last_entry_at = datetime.utcnow()
        db.session.commit()
    
    def can_create_entry(self, user_subscription_tier='free'):
        """Check if user can create another entry based on their tier"""
        limits = {
            'free': 5,
            'premium': float('inf'),  # Unlimited
            'pro': float('inf')  # For future tiers
        }
        
        limit = limits.get(user_subscription_tier, 5)
        return self.entry_count < limit
    
    def get_remaining_entries(self, user_subscription_tier='free'):
        """Get number of remaining entries for the month"""
        limits = {
            'free': 5,
            'premium': float('inf'),
            'pro': float('inf')
        }
        
        limit = limits.get(user_subscription_tier, 5)
        if limit == float('inf'):
            return 'unlimited'
        
        remaining = limit - self.entry_count
        return max(0, remaining)
    
    def to_dict(self, user_subscription_tier='free'):
        """Convert to dictionary"""
        return {
            'month_year': self.month_year,
            'entry_count': self.entry_count,
            'last_entry_at': self.last_entry_at.isoformat() if self.last_entry_at else None,
            'remaining_entries': self.get_remaining_entries(user_subscription_tier),
            'can_create_entry': self.can_create_entry(user_subscription_tier)
        }
    
    def __repr__(self):
        return f'<UsageTracking user_id={self.user_id} month={self.month_year} count={self.entry_count}>'