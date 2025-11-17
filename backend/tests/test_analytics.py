"""
Tests for analytics endpoints
"""
import pytest
import json
from datetime import datetime, timedelta
from app.models import JournalEntry


class TestMoodHistory:
    """Test mood history endpoint"""

    def test_mood_history_empty_data(self, client, test_user, auth_headers):
        """Test mood history with no entries"""
        response = client.get('/api/analytics/mood-history', headers=auth_headers)

        assert response.status_code == 200
        assert 'data' in response.json
        assert 'summary' in response.json
        assert len(response.json['data']) == 0
        assert response.json['summary']['total_entries'] == 0
        assert response.json['summary']['trend'] == 'no_data'

    def test_mood_history_single_entry(self, client, db_session, test_user, auth_headers):
        """Test mood history with single entry"""
        entry = JournalEntry(
            user_id=test_user.id,
            title='Test Entry',
            mood_score=7,
            processing_status='completed'
        )
        db_session.add(entry)
        db_session.commit()

        response = client.get('/api/analytics/mood-history', headers=auth_headers)

        assert response.status_code == 200
        assert len(response.json['data']) == 1
        assert response.json['data'][0]['avg_mood'] == 7.0
        assert response.json['summary']['overall_avg'] == 7.0
        assert response.json['summary']['total_entries'] == 1

    def test_mood_history_7_days(self, client, db_session, test_user, auth_headers):
        """Test mood history with 7 day filter"""
        # Create entries spread across different dates
        today = datetime.utcnow()
        for i in range(10):
            entry = JournalEntry(
                user_id=test_user.id,
                title=f'Entry {i}',
                mood_score=5 + i % 5,
                processing_status='completed',
                created_at=today - timedelta(days=i)
            )
            db_session.add(entry)
        db_session.commit()

        response = client.get('/api/analytics/mood-history?days=7', headers=auth_headers)

        assert response.status_code == 200
        # Should only get entries from last 7 days (not all 10)
        assert len(response.json['data']) <= 7

    def test_mood_history_30_days(self, client, db_session, test_user, auth_headers):
        """Test mood history with 30 day filter (default)"""
        today = datetime.utcnow()
        for i in range(5):
            entry = JournalEntry(
                user_id=test_user.id,
                title=f'Entry {i}',
                mood_score=6,
                processing_status='completed',
                created_at=today - timedelta(days=i * 2)
            )
            db_session.add(entry)
        db_session.commit()

        response = client.get('/api/analytics/mood-history', headers=auth_headers)

        assert response.status_code == 200
        assert response.json['summary']['total_entries'] == 5

    def test_mood_history_null_mood_scores(self, client, db_session, test_user, auth_headers):
        """Test mood history filters out null mood scores"""
        entry1 = JournalEntry(
            user_id=test_user.id,
            title='With Mood',
            mood_score=8,
            processing_status='completed'
        )
        entry2 = JournalEntry(
            user_id=test_user.id,
            title='Without Mood',
            mood_score=None,
            processing_status='completed'
        )
        db_session.add_all([entry1, entry2])
        db_session.commit()

        response = client.get('/api/analytics/mood-history', headers=auth_headers)

        assert response.status_code == 200
        # Should only count entry with mood_score
        assert response.json['summary']['total_entries'] == 1

    def test_mood_history_trend_improving(self, client, db_session, test_user, auth_headers):
        """Test trend calculation - improving"""
        today = datetime.utcnow()
        # First half: low moods
        for i in range(4):
            entry = JournalEntry(
                user_id=test_user.id,
                title=f'Low Entry {i}',
                mood_score=4,
                processing_status='completed',
                created_at=today - timedelta(days=8 + i)
            )
            db_session.add(entry)

        # Second half: high moods
        for i in range(4):
            entry = JournalEntry(
                user_id=test_user.id,
                title=f'High Entry {i}',
                mood_score=8,
                processing_status='completed',
                created_at=today - timedelta(days=i)
            )
            db_session.add(entry)
        db_session.commit()

        response = client.get('/api/analytics/mood-history', headers=auth_headers)

        assert response.status_code == 200
        assert response.json['summary']['trend'] == 'improving'

    def test_mood_history_deleted_entries_excluded(self, client, db_session, test_user, auth_headers):
        """Test that deleted entries are excluded"""
        entry1 = JournalEntry(
            user_id=test_user.id,
            title='Active',
            mood_score=7,
            processing_status='completed'
        )
        entry2 = JournalEntry(
            user_id=test_user.id,
            title='Deleted',
            mood_score=9,
            processing_status='completed',
            is_deleted=True
        )
        db_session.add_all([entry1, entry2])
        db_session.commit()

        response = client.get('/api/analytics/mood-history', headers=auth_headers)

        assert response.status_code == 200
        assert response.json['summary']['total_entries'] == 1
        assert response.json['summary']['overall_avg'] == 7.0


class TestEmotionTrends:
    """Test emotion trends endpoint"""

    def test_emotion_trends_empty_data(self, client, test_user, auth_headers):
        """Test emotion trends with no entries"""
        response = client.get('/api/analytics/emotion-trends', headers=auth_headers)

        assert response.status_code == 200
        assert 'emotions' in response.json
        assert len(response.json['emotions']) == 0
        assert response.json['total_emotion_mentions'] == 0

    def test_emotion_trends_aggregation(self, client, db_session, test_user, auth_headers):
        """Test emotion aggregation and counting"""
        emotions1 = json.dumps([
            {'name': 'happy', 'confidence': 0.9},
            {'name': 'excited', 'confidence': 0.7}
        ])
        emotions2 = json.dumps([
            {'name': 'happy', 'confidence': 0.8},
            {'name': 'anxious', 'confidence': 0.6}
        ])

        entry1 = JournalEntry(
            user_id=test_user.id,
            title='Entry 1',
            emotions=emotions1,
            processing_status='completed'
        )
        entry2 = JournalEntry(
            user_id=test_user.id,
            title='Entry 2',
            emotions=emotions2,
            processing_status='completed'
        )
        db_session.add_all([entry1, entry2])
        db_session.commit()

        response = client.get('/api/analytics/emotion-trends', headers=auth_headers)

        assert response.status_code == 200
        assert response.json['total_emotion_mentions'] == 4
        assert response.json['unique_emotions'] == 3

        # Find 'happy' emotion
        happy_emotion = next(e for e in response.json['emotions'] if e['name'] == 'happy')
        assert happy_emotion['count'] == 2
        assert happy_emotion['percentage'] == 50.0

    def test_emotion_trends_malformed_json(self, client, db_session, test_user, auth_headers):
        """Test that malformed emotion JSON is handled gracefully"""
        entry1 = JournalEntry(
            user_id=test_user.id,
            title='Valid',
            emotions=json.dumps([{'name': 'happy', 'confidence': 0.9}]),
            processing_status='completed'
        )
        entry2 = JournalEntry(
            user_id=test_user.id,
            title='Invalid JSON',
            emotions='not-valid-json{',
            processing_status='completed'
        )
        db_session.add_all([entry1, entry2])
        db_session.commit()

        response = client.get('/api/analytics/emotion-trends', headers=auth_headers)

        assert response.status_code == 200
        # Should only process valid entry
        assert response.json['total_emotion_mentions'] == 1

    def test_emotion_trends_confidence_averaging(self, client, db_session, test_user, auth_headers):
        """Test average confidence calculation"""
        emotions = json.dumps([
            {'name': 'happy', 'confidence': 0.9},
            {'name': 'happy', 'confidence': 0.7}
        ])

        entry = JournalEntry(
            user_id=test_user.id,
            title='Entry',
            emotions=emotions,
            processing_status='completed'
        )
        db_session.add(entry)
        db_session.commit()

        response = client.get('/api/analytics/emotion-trends', headers=auth_headers)

        assert response.status_code == 200
        happy_emotion = response.json['emotions'][0]
        assert happy_emotion['avg_confidence'] == 0.8


class TestMoodByWeekday:
    """Test mood by weekday endpoint"""

    def test_mood_by_weekday_empty_data(self, client, test_user, auth_headers):
        """Test mood by weekday with no entries"""
        response = client.get('/api/analytics/mood-by-weekday', headers=auth_headers)

        assert response.status_code == 200
        assert 'data' in response.json
        assert len(response.json['data']) == 7  # All 7 weekdays
        # All should have null mood
        assert all(d['avg_mood'] is None for d in response.json['data'])

    def test_mood_by_weekday_calculation(self, client, db_session, test_user, auth_headers):
        """Test weekday mood calculation"""
        today = datetime.utcnow()

        # Create entries for specific weekdays
        # Find next Monday (weekday = 0)
        days_until_monday = (7 - today.weekday()) % 7
        next_monday = today + timedelta(days=days_until_monday if days_until_monday != 0 else 7)

        # Create Monday entries
        for i in range(3):
            entry = JournalEntry(
                user_id=test_user.id,
                title=f'Monday {i}',
                mood_score=6,
                processing_status='completed',
                created_at=next_monday - timedelta(weeks=i)
            )
            db_session.add(entry)
        db_session.commit()

        response = client.get('/api/analytics/mood-by-weekday', headers=auth_headers)

        assert response.status_code == 200
        monday_data = next(d for d in response.json['data'] if d['weekday'] == 'Monday')
        assert monday_data['avg_mood'] == 6.0
        assert monday_data['entry_count'] == 3

    def test_mood_by_weekday_insights(self, client, db_session, test_user, auth_headers):
        """Test insights generation for weekday patterns"""
        today = datetime.utcnow()

        # Create entries with clear pattern (high on Friday, low on Monday)
        for week in range(5):
            # Monday - low mood
            monday = today - timedelta(days=today.weekday(), weeks=week)
            entry_low = JournalEntry(
                user_id=test_user.id,
                title=f'Monday Week {week}',
                mood_score=4,
                processing_status='completed',
                created_at=monday
            )
            db_session.add(entry_low)

            # Friday - high mood
            friday = monday + timedelta(days=4)
            entry_high = JournalEntry(
                user_id=test_user.id,
                title=f'Friday Week {week}',
                mood_score=9,
                processing_status='completed',
                created_at=friday
            )
            db_session.add(entry_high)

        db_session.commit()

        response = client.get('/api/analytics/mood-by-weekday', headers=auth_headers)

        assert response.status_code == 200
        # Should generate insights due to significant difference
        assert len(response.json['insights']) > 0


class TestWordFrequency:
    """Test word frequency endpoint"""

    def test_word_frequency_empty_data(self, client, test_user, auth_headers):
        """Test word frequency with no entries"""
        response = client.get('/api/analytics/word-frequency', headers=auth_headers)

        assert response.status_code == 200
        assert len(response.json['words']) == 0
        assert response.json['total_words'] == 0

    def test_word_frequency_stopword_filtering(self, client, db_session, test_user, auth_headers):
        """Test that stopwords are filtered out"""
        entry = JournalEntry(
            user_id=test_user.id,
            title='Entry',
            formatted_content='I am feeling happy today and I think that is great',
            processing_status='completed'
        )
        db_session.add(entry)
        db_session.commit()

        response = client.get('/api/analytics/word-frequency', headers=auth_headers)

        assert response.status_code == 200
        # Common words should be in the results
        word_list = [w['word'] for w in response.json['words']]
        # 'happy' and 'great' should be included
        assert 'happy' in word_list or 'great' in word_list
        # Stopwords should be excluded
        assert 'the' not in word_list
        assert 'and' not in word_list

    def test_word_frequency_mood_correlation(self, client, db_session, test_user, auth_headers):
        """Test mood correlation calculation"""
        entry1 = JournalEntry(
            user_id=test_user.id,
            title='Entry 1',
            formatted_content='work stress deadline',
            mood_score=4,
            processing_status='completed'
        )
        entry2 = JournalEntry(
            user_id=test_user.id,
            title='Entry 2',
            formatted_content='work success achievement',
            mood_score=8,
            processing_status='completed'
        )
        db_session.add_all([entry1, entry2])
        db_session.commit()

        response = client.get('/api/analytics/word-frequency', headers=auth_headers)

        assert response.status_code == 200
        # Find 'work' in results
        work_word = next((w for w in response.json['words'] if w['word'] == 'work'), None)
        if work_word:
            # Average mood when 'work' is mentioned should be 6.0 (4+8)/2
            assert work_word['avg_mood_when_mentioned'] == 6.0

    def test_word_frequency_limit_parameter(self, client, db_session, test_user, auth_headers):
        """Test limit parameter"""
        # Create entry with many words
        entry = JournalEntry(
            user_id=test_user.id,
            title='Entry',
            formatted_content=' '.join([f'word{i}' for i in range(100)]),
            processing_status='completed'
        )
        db_session.add(entry)
        db_session.commit()

        response = client.get('/api/analytics/word-frequency?limit=10', headers=auth_headers)

        assert response.status_code == 200
        # Should respect limit
        assert len(response.json['words']) <= 10

    def test_word_frequency_minimum_length(self, client, db_session, test_user, auth_headers):
        """Test that short words are filtered (min 3 chars)"""
        entry = JournalEntry(
            user_id=test_user.id,
            title='Entry',
            formatted_content='I am at my house today',
            processing_status='completed'
        )
        db_session.add(entry)
        db_session.commit()

        response = client.get('/api/analytics/word-frequency', headers=auth_headers)

        assert response.status_code == 200
        word_list = [w['word'] for w in response.json['words']]
        # 2-letter words should be excluded
        assert 'am' not in word_list
        assert 'at' not in word_list
        assert 'my' not in word_list


class TestAnalyticsAuthentication:
    """Test authentication requirements for analytics endpoints"""

    def test_mood_history_requires_auth(self, client):
        """Test that mood history requires authentication"""
        response = client.get('/api/analytics/mood-history')
        assert response.status_code == 401

    def test_emotion_trends_requires_auth(self, client):
        """Test that emotion trends requires authentication"""
        response = client.get('/api/analytics/emotion-trends')
        assert response.status_code == 401

    def test_mood_by_weekday_requires_auth(self, client):
        """Test that mood by weekday requires authentication"""
        response = client.get('/api/analytics/mood-by-weekday')
        assert response.status_code == 401

    def test_word_frequency_requires_auth(self, client):
        """Test that word frequency requires authentication"""
        response = client.get('/api/analytics/word-frequency')
        assert response.status_code == 401
