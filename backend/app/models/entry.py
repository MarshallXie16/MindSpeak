from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from app.models.user import db

class JournalEntry(db.Model):
    __tablename__ = 'journal_entries'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Core content
    title = Column(String(255))
    raw_transcript = Column(Text)
    formatted_content = Column(Text)
    
    # Mood and emotions
    mood_score = Column(Integer)  # 1-10 scale
    emotions = Column(JSON)  # JSON array of emotions with confidence scores
    
    # AI insights
    insights = Column(Text)
    
    # Audio file reference
    audio_filename = Column(String(255))
    
    # Processing status
    processing_status = Column(String(20), default='pending')  # pending, processing, completed, error
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    entry_date = Column(DateTime, default=datetime.utcnow)  # User can set custom date
    
    # Soft delete
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime)
    
    def soft_delete(self):
        """Soft delete the entry"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        db.session.commit()
    
    def restore(self):
        """Restore a soft-deleted entry"""
        self.is_deleted = False
        self.deleted_at = None
        db.session.commit()
    
    @classmethod
    def get_active_entries(cls, user_id, limit=None, offset=0):
        """Get all active (non-deleted) entries for a user"""
        query = cls.query.filter_by(
            user_id=user_id,
            is_deleted=False
        ).order_by(cls.entry_date.desc())
        
        if limit:
            query = query.limit(limit).offset(offset)
        
        return query.all()
    
    @classmethod
    def get_entries_by_date_range(cls, user_id, start_date, end_date):
        """Get entries within a date range"""
        return cls.query.filter(
            cls.user_id == user_id,
            cls.is_deleted == False,
            cls.entry_date >= start_date,
            cls.entry_date <= end_date
        ).order_by(cls.entry_date.desc()).all()
    
    def get_mood_emoji(self):
        """Return an emoji representation of the mood score"""
        if not self.mood_score:
            return "😐"
        
        mood_emojis = {
            1: "😢", 2: "😔", 3: "😕", 4: "😐", 5: "🙂",
            6: "😊", 7: "😄", 8: "😃", 9: "😁", 10: "🤗"
        }
        return mood_emojis.get(self.mood_score, "😐")
    
    def get_word_count(self):
        """Get word count of the formatted content"""
        if not self.formatted_content:
            return 0
        return len(self.formatted_content.split())
    
    def get_top_emotions(self, limit=3):
        """Get the top emotions with highest confidence"""
        if not self.emotions:
            return []
        
        # Handle both JSON string and list formats
        import json
        emotions_list = self.emotions
        if isinstance(emotions_list, str):
            try:
                emotions_list = json.loads(emotions_list)
            except (json.JSONDecodeError, TypeError):
                return []
        
        if not isinstance(emotions_list, list):
            return []
        
        # Sort emotions by confidence
        sorted_emotions = sorted(emotions_list, key=lambda x: x.get('confidence', 0) if isinstance(x, dict) else 0, reverse=True)
        return sorted_emotions[:limit]
    
    def to_dict(self, include_content=True):
        """Convert entry object to dictionary"""
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'mood_score': self.mood_score,
            'mood_emoji': self.get_mood_emoji(),
            'emotions': self.emotions,
            'top_emotions': self.get_top_emotions(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'entry_date': self.entry_date.isoformat() if self.entry_date else None,
            'has_audio': bool(self.audio_filename),
            'word_count': self.get_word_count()
        }
        
        if include_content:
            result.update({
                'raw_transcript': self.raw_transcript,
                'formatted_content': self.formatted_content,
                'insights': self.insights
            })
        
        return result
    
    def __repr__(self):
        return f'<JournalEntry {self.id}: {self.title or "Untitled"}>'