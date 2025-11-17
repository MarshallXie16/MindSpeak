"""
Tests for journal entry endpoints
"""
import pytest
import json
from app.models import JournalEntry, UsageTracking


class TestEntryEndpoints:
    """Test journal entry CRUD operations"""

    def test_get_entries_empty(self, client, auth_headers):
        """Test getting entries when none exist"""
        response = client.get('/api/entries', headers=auth_headers)

        assert response.status_code == 200
        assert 'entries' in response.json
        assert len(response.json['entries']) == 0

    def test_get_entries_with_data(self, client, auth_headers, test_user, db_session):
        """Test getting entries with existing data"""
        # Create test entries
        entry1 = JournalEntry(
            user_id=test_user.id,
            title='Entry 1',
            processing_status='completed',
            mood_score=7
        )
        entry2 = JournalEntry(
            user_id=test_user.id,
            title='Entry 2',
            processing_status='completed',
            mood_score=5
        )
        db_session.add_all([entry1, entry2])
        db_session.commit()

        response = client.get('/api/entries', headers=auth_headers)

        assert response.status_code == 200
        assert len(response.json['entries']) == 2

    def test_get_single_entry(self, client, auth_headers, test_user, db_session):
        """Test getting a single entry by ID"""
        entry = JournalEntry(
            user_id=test_user.id,
            title='Test Entry',
            formatted_content='Test content',
            processing_status='completed'
        )
        db_session.add(entry)
        db_session.commit()

        response = client.get(f'/api/entries/{entry.id}', headers=auth_headers)

        assert response.status_code == 200
        assert response.json['entry']['title'] == 'Test Entry'
        assert response.json['entry']['formatted_content'] == 'Test content'

    def test_get_nonexistent_entry(self, client, auth_headers):
        """Test getting entry that doesn't exist"""
        response = client.get('/api/entries/99999', headers=auth_headers)

        assert response.status_code == 404

    def test_update_entry(self, client, auth_headers, test_user, db_session):
        """Test updating an entry"""
        entry = JournalEntry(
            user_id=test_user.id,
            title='Original Title',
            formatted_content='Original content',
            processing_status='completed'
        )
        db_session.add(entry)
        db_session.commit()

        response = client.put(
            f'/api/entries/{entry.id}',
            headers=auth_headers,
            json={
                'title': 'Updated Title',
                'formatted_content': 'Updated content'
            }
        )

        assert response.status_code == 200
        assert response.json['entry']['title'] == 'Updated Title'

        # Verify in database
        db_session.refresh(entry)
        assert entry.title == 'Updated Title'
        assert entry.formatted_content == 'Updated content'

    def test_delete_entry(self, client, auth_headers, test_user, db_session):
        """Test soft deleting an entry"""
        entry = JournalEntry(
            user_id=test_user.id,
            title='To Delete',
            processing_status='completed'
        )
        db_session.add(entry)
        db_session.commit()
        entry_id = entry.id

        response = client.delete(f'/api/entries/{entry_id}', headers=auth_headers)

        assert response.status_code == 200

        # Verify soft deleted
        db_session.refresh(entry)
        assert entry.is_deleted is True
        assert entry.deleted_at is not None

    def test_get_dashboard_stats(self, client, auth_headers, test_user, db_session):
        """Test getting dashboard statistics"""
        # Create test entries
        entry1 = JournalEntry(
            user_id=test_user.id,
            title='Entry 1',
            processing_status='completed',
            mood_score=7
        )
        entry2 = JournalEntry(
            user_id=test_user.id,
            title='Entry 2',
            processing_status='completed',
            mood_score=9
        )
        db_session.add_all([entry1, entry2])
        db_session.commit()

        response = client.get('/api/entries/stats', headers=auth_headers)

        assert response.status_code == 200
        assert 'stats' in response.json
        assert response.json['stats']['total_entries'] == 2
        assert response.json['stats']['mood_average'] == 8.0  # (7 + 9) / 2


class TestUsageLimits:
    """Test usage limit enforcement"""

    def test_usage_limit_free_tier(self, client, auth_headers, test_user, db_session):
        """Test that free tier is limited to 5 entries per month"""
        # Get or create usage tracking
        usage = UsageTracking.get_or_create_current_month(test_user.id)

        # Create 5 entries (max for free tier)
        for i in range(5):
            usage.increment_usage()
        db_session.commit()

        # Attempt to upload 6th entry should fail
        # (This would require actually uploading audio, which we're mocking here)
        # Just verify the logic works
        assert usage.can_create_entry('free') is False
        assert usage.get_remaining_entries('free') == 0
