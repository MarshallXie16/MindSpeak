from sqlalchemy import Column, Integer, String, Boolean, Time, ForeignKey, JSON, Text
from app.models.user import db

class UserPreferences(db.Model):
    __tablename__ = 'user_preferences'
    
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    
    # AI interaction preferences
    custom_ai_instructions = Column(Text)  # User's custom instructions for AI behavior
    
    # Goals tracking
    goals = Column(JSON)  # [{"id": 1, "text": "I want to become more positive", "created_at": "2024-01-01"}]
    
    # Reminder settings
    reminder_enabled = Column(Boolean, default=False)
    reminder_time = Column(Time)  # Daily reminder time
    reminder_days = Column(JSON)  # ["monday", "tuesday", ...] for which days to remind
    
    # UI preferences
    theme = Column(String(20), default='light')  # light, dark, auto
    
    # Streak tracking
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_entry_date = Column(String(10))  # YYYY-MM-DD format for easy comparison
    
    def update_streak(self, entry_date):
        """Update streak based on new entry date"""
        from datetime import datetime, timedelta
        
        today = entry_date.strftime('%Y-%m-%d')
        
        if not self.last_entry_date:
            # First entry
            self.current_streak = 1
            self.longest_streak = 1
            self.last_entry_date = today
        else:
            last_date = datetime.strptime(self.last_entry_date, '%Y-%m-%d').date()
            current_date = entry_date.date()
            
            if current_date == last_date:
                # Already journaled today
                pass
            elif current_date == last_date + timedelta(days=1):
                # Consecutive day
                self.current_streak += 1
                self.longest_streak = max(self.longest_streak, self.current_streak)
                self.last_entry_date = today
            elif current_date > last_date:
                # Streak broken
                self.current_streak = 1
                self.last_entry_date = today
    
    def add_goal(self, goal_text):
        """Add a new goal"""
        from datetime import datetime
        
        if not self.goals:
            self.goals = []
        
        new_goal = {
            "id": len(self.goals) + 1,
            "text": goal_text,
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.goals.append(new_goal)
    
    def remove_goal(self, goal_id):
        """Remove a goal by ID"""
        if self.goals:
            self.goals = [g for g in self.goals if g.get('id') != goal_id]
    
    def to_dict(self):
        """Convert preferences to dictionary"""
        return {
            'custom_ai_instructions': self.custom_ai_instructions,
            'goals': self.goals or [],
            'reminder_enabled': self.reminder_enabled,
            'reminder_time': self.reminder_time.strftime('%H:%M') if self.reminder_time else None,
            'reminder_days': self.reminder_days or [],
            'theme': self.theme,
            'current_streak': self.current_streak,
            'longest_streak': self.longest_streak
        }
    
    def __repr__(self):
        return f'<UserPreferences for user_id={self.user_id}>'