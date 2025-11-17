"""
Tests for database models
"""
import pytest
from datetime import datetime, timedelta
from app.models import User, JournalEntry, UserPreferences, UsageTracking


class TestUserModel:
    """Test User model"""

    def test_create_user(self, db_session):
        """Test creating a user"""
        user = User(email='test@example.com', username='testuser')
        user.set_password('password123')
        db_session.add(user)
        db_session.commit()

        assert user.id is not None
        assert user.email == 'test@example.com'
        assert user.username == 'testuser'
        assert user.check_password('password123')
        assert not user.check_password('wrongpassword')

    def test_user_display_name(self, db_session):
        """Test user display name fallback"""
        # With display_name set
        user1 = User(email='user1@example.com', display_name='Display Name')
        assert user1.get_display_name() == 'Display Name'

        # With username only
        user2 = User(email='user2@example.com', username='username')
        assert user2.get_display_name() == 'username'

        # With email only
        user3 = User(email='user3@example.com')
        assert user3.get_display_name() == 'user3'

    def test_user_to_dict(self, test_user):
        """Test user serialization"""
        user_dict = test_user.to_dict()

        assert 'id' in user_dict
        assert 'email' in user_dict
        assert 'password_hash' not in user_dict  # Should not expose password
        assert user_dict['email'] == 'test@example.com'


class TestJournalEntryModel:
    """Test JournalEntry model"""

    def test_create_entry(self, db_session, test_user):
        """Test creating a journal entry"""
        entry = JournalEntry(
            user_id=test_user.id,
            title='Test Entry',
            raw_transcript='This is a test transcript',
            formatted_content='This is formatted content',
            mood_score=7,
            processing_status='completed'
        )
        db_session.add(entry)
        db_session.commit()

        assert entry.id is not None
        assert entry.user_id == test_user.id
        assert entry.mood_score == 7

    def test_soft_delete(self, db_session, test_user):
        """Test soft delete functionality"""
        entry = JournalEntry(
            user_id=test_user.id,
            title='Test Entry',
            processing_status='completed'
        )
        db_session.add(entry)
        db_session.commit()

        # Soft delete
        entry.soft_delete()

        assert entry.is_deleted is True
        assert entry.deleted_at is not None

    def test_get_active_entries(self, db_session, test_user):
        """Test getting only active entries"""
        # Create active entry
        active = JournalEntry(user_id=test_user.id, title='Active', processing_status='completed')
        db_session.add(active)

        # Create deleted entry
        deleted = JournalEntry(user_id=test_user.id, title='Deleted', processing_status='completed', is_deleted=True)
        db_session.add(deleted)
        db_session.commit()

        active_entries = JournalEntry.get_active_entries(test_user.id)

        assert len(active_entries) == 1
        assert active_entries[0].title == 'Active'

    def test_mood_emoji(self, db_session, test_user):
        """Test mood emoji generation"""
        entry = JournalEntry(user_id=test_user.id, mood_score=8)
        db_session.add(entry)
        db_session.commit()

        emoji = entry.get_mood_emoji()
        assert emoji in ['😢', '😔', '😕', '😐', '🙂', '😊', '😄', '😃', '😁', '🤗']


class TestUserPreferencesModel:
    """Test UserPreferences model"""

    def test_create_preferences(self, db_session, test_user):
        """Test creating user preferences"""
        prefs = UserPreferences(
            user_id=test_user.id,
            custom_ai_instructions='Be concise',
            theme='dark'
        )
        db_session.add(prefs)
        db_session.commit()

        assert prefs.user_id == test_user.id
        assert prefs.custom_ai_instructions == 'Be concise'

    def test_streak_tracking(self, db_session, test_user):
        """Test streak update logic"""
        prefs = UserPreferences(user_id=test_user.id)
        db_session.add(prefs)
        db_session.commit()

        # First entry
        today = datetime.utcnow()
        prefs.update_streak(today)
        assert prefs.current_streak == 1
        assert prefs.longest_streak == 1

        # Consecutive day
        tomorrow = today + timedelta(days=1)
        prefs.update_streak(tomorrow)
        assert prefs.current_streak == 2
        assert prefs.longest_streak == 2

        # Broken streak
        future = today + timedelta(days=5)
        prefs.update_streak(future)
        assert prefs.current_streak == 1  # Reset
        assert prefs.longest_streak == 2  # Preserved

    def test_goal_management(self, db_session, test_user):
        """Test adding and removing goals"""
        prefs = UserPreferences(user_id=test_user.id)
        db_session.add(prefs)
        db_session.commit()

        # Add goal
        prefs.add_goal('Be more positive')
        db_session.commit()

        assert len(prefs.goals) == 1
        assert prefs.goals[0]['text'] == 'Be more positive'

        # Remove goal
        goal_id = prefs.goals[0]['id']
        prefs.remove_goal(goal_id)
        db_session.commit()

        assert len(prefs.goals) == 0


class TestUsageTrackingModel:
    """Test UsageTracking model"""

    def test_create_usage_tracking(self, db_session, test_user):
        """Test creating usage tracking"""
        usage = UsageTracking.get_or_create_current_month(test_user.id)

        assert usage.user_id == test_user.id
        assert usage.entry_count == 0

    def test_increment_usage(self, db_session, test_user):
        """Test incrementing usage count"""
        usage = UsageTracking.get_or_create_current_month(test_user.id)

        usage.increment_usage()
        assert usage.entry_count == 1

        usage.increment_usage()
        assert usage.entry_count == 2

    def test_usage_limits(self, db_session, test_user):
        """Test usage limit checking"""
        usage = UsageTracking.get_or_create_current_month(test_user.id)

        # Free tier: 5 entries
        assert usage.can_create_entry('free') is True

        # Add 5 entries
        for _ in range(5):
            usage.increment_usage()

        # Should now be blocked
        assert usage.can_create_entry('free') is False

        # Premium should still work
        assert usage.can_create_entry('premium') is True
