"""
Analytics endpoints for data visualization dashboard
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, JournalEntry
from sqlalchemy import func, extract, case
from datetime import datetime, timedelta
import json
from collections import Counter
import re

bp = Blueprint('analytics', __name__)

# Common English stopwords to filter from word frequency
STOPWORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've",
    "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his',
    'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself',
    'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom',
    'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were',
    'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did',
    'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
    'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into',
    'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up',
    'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then',
    'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'both', 'each',
    'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
    'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just',
    'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've',
    'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn',
    "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn',
    "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't",
    'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't",
    'won', "won't", 'wouldn', "wouldn't", 'today', 'feel', 'feeling', 'felt', 'think',
    'thought', 'day', 'time', 'really', 'still', 'like', 'want', 'know', 'get', 'going'
}


@bp.route('/mood-history', methods=['GET'])
@jwt_required()
def get_mood_history():
    """
    Get mood history over time

    Query params:
        days (int): Number of days to look back (default: 30, options: 7, 30, 90)

    Returns mood trend data grouped by date
    """
    user_id = int(get_jwt_identity())
    days = request.args.get('days', 30, type=int)

    # Validate days parameter
    if days not in [7, 30, 90]:
        days = 30

    # Calculate start date
    start_date = datetime.utcnow() - timedelta(days=days)

    # Query mood data grouped by date
    mood_data = db.session.query(
        func.date(JournalEntry.created_at).label('date'),
        func.avg(JournalEntry.mood_score).label('avg_mood'),
        func.count(JournalEntry.id).label('entry_count'),
        func.min(JournalEntry.mood_score).label('min_mood'),
        func.max(JournalEntry.mood_score).label('max_mood')
    ).filter(
        JournalEntry.user_id == user_id,
        JournalEntry.is_deleted == False,
        JournalEntry.mood_score.isnot(None),
        JournalEntry.created_at >= start_date
    ).group_by(
        func.date(JournalEntry.created_at)
    ).order_by(
        func.date(JournalEntry.created_at).asc()
    ).all()

    # Format response
    data = []
    for row in mood_data:
        data.append({
            'date': str(row.date) if row.date else None,
            'avg_mood': round(row.avg_mood, 1) if row.avg_mood else None,
            'entry_count': row.entry_count,
            'min_mood': row.min_mood,
            'max_mood': row.max_mood
        })

    # Calculate summary statistics
    if data:
        overall_avg = sum(d['avg_mood'] for d in data if d['avg_mood']) / len([d for d in data if d['avg_mood']])
        total_entries = sum(d['entry_count'] for d in data)
        days_with_entries = len(data)

        # Simple trend calculation (compare first half vs second half)
        if len(data) >= 4:
            mid = len(data) // 2
            first_half_avg = sum(d['avg_mood'] for d in data[:mid] if d['avg_mood']) / len([d for d in data[:mid] if d['avg_mood']])
            second_half_avg = sum(d['avg_mood'] for d in data[mid:] if d['avg_mood']) / len([d for d in data[mid:] if d['avg_mood']])

            if second_half_avg > first_half_avg + 0.5:
                trend = 'improving'
            elif second_half_avg < first_half_avg - 0.5:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'

        summary = {
            'overall_avg': round(overall_avg, 1),
            'total_entries': total_entries,
            'days_with_entries': days_with_entries,
            'trend': trend
        }
    else:
        summary = {
            'overall_avg': None,
            'total_entries': 0,
            'days_with_entries': 0,
            'trend': 'no_data'
        }

    return jsonify({
        'data': data,
        'summary': summary
    }), 200


@bp.route('/emotion-trends', methods=['GET'])
@jwt_required()
def get_emotion_trends():
    """
    Get emotion frequency trends

    Query params:
        days (int): Number of days to look back (default: 30)

    Returns aggregated emotion data
    """
    user_id = int(get_jwt_identity())
    days = request.args.get('days', 30, type=int)

    start_date = datetime.utcnow() - timedelta(days=days)

    # Get entries with emotions
    entries = JournalEntry.query.filter(
        JournalEntry.user_id == user_id,
        JournalEntry.is_deleted == False,
        JournalEntry.emotions.isnot(None),
        JournalEntry.created_at >= start_date
    ).all()

    # Aggregate emotions
    emotion_counts = {}
    emotion_confidences = {}

    for entry in entries:
        try:
            # Parse emotions (stored as JSON string or already parsed)
            if isinstance(entry.emotions, str):
                emotions = json.loads(entry.emotions)
            else:
                emotions = entry.emotions

            if isinstance(emotions, list):
                for emotion in emotions:
                    if isinstance(emotion, dict) and 'name' in emotion:
                        name = emotion['name'].lower()
                        confidence = emotion.get('confidence', 1.0)

                        if name not in emotion_counts:
                            emotion_counts[name] = 0
                            emotion_confidences[name] = []

                        emotion_counts[name] += 1
                        emotion_confidences[name].append(confidence)
        except (json.JSONDecodeError, TypeError, AttributeError):
            # Skip malformed emotion data
            continue

    # Calculate totals
    total_emotion_mentions = sum(emotion_counts.values())

    # Format response
    emotions_data = []
    for name, count in emotion_counts.items():
        avg_confidence = sum(emotion_confidences[name]) / len(emotion_confidences[name])
        percentage = (count / total_emotion_mentions * 100) if total_emotion_mentions > 0 else 0

        emotions_data.append({
            'name': name,
            'count': count,
            'percentage': round(percentage, 1),
            'avg_confidence': round(avg_confidence, 2)
        })

    # Sort by count descending
    emotions_data.sort(key=lambda x: x['count'], reverse=True)

    return jsonify({
        'emotions': emotions_data,
        'total_emotion_mentions': total_emotion_mentions,
        'unique_emotions': len(emotion_counts)
    }), 200


@bp.route('/mood-by-weekday', methods=['GET'])
@jwt_required()
def get_mood_by_weekday():
    """
    Get average mood by day of week

    Query params:
        days (int): Number of days to look back (default: 90)

    Returns mood averages for each weekday
    """
    user_id = int(get_jwt_identity())
    days = request.args.get('days', 90, type=int)

    start_date = datetime.utcnow() - timedelta(days=days)

    # Query mood by weekday (0 = Monday, 6 = Sunday in Python, but strftime %w gives 0 = Sunday)
    # We'll use Python's weekday() method in post-processing for consistency
    entries = JournalEntry.query.filter(
        JournalEntry.user_id == user_id,
        JournalEntry.is_deleted == False,
        JournalEntry.mood_score.isnot(None),
        JournalEntry.created_at >= start_date
    ).all()

    # Group by weekday
    weekday_data = {i: {'moods': [], 'count': 0} for i in range(7)}

    for entry in entries:
        weekday_num = entry.created_at.weekday()  # 0 = Monday, 6 = Sunday
        weekday_data[weekday_num]['moods'].append(entry.mood_score)
        weekday_data[weekday_num]['count'] += 1

    # Calculate averages
    weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    data = []

    for i in range(7):
        if weekday_data[i]['count'] > 0:
            avg_mood = sum(weekday_data[i]['moods']) / weekday_data[i]['count']
            data.append({
                'weekday': weekday_names[i],
                'weekday_num': i,
                'avg_mood': round(avg_mood, 1),
                'entry_count': weekday_data[i]['count']
            })
        else:
            data.append({
                'weekday': weekday_names[i],
                'weekday_num': i,
                'avg_mood': None,
                'entry_count': 0
            })

    # Generate insights
    insights = []
    valid_data = [d for d in data if d['avg_mood'] is not None]

    if valid_data:
        highest = max(valid_data, key=lambda x: x['avg_mood'])
        lowest = min(valid_data, key=lambda x: x['avg_mood'])

        if highest['avg_mood'] - lowest['avg_mood'] > 1.0:  # Significant difference
            insights.append(f"Your mood is highest on {highest['weekday']}s ({highest['avg_mood']}/10)")
            insights.append(f"Your mood tends to dip on {lowest['weekday']}s ({lowest['avg_mood']}/10)")

    return jsonify({
        'data': data,
        'insights': insights
    }), 200


@bp.route('/word-frequency', methods=['GET'])
@jwt_required()
def get_word_frequency():
    """
    Get most common words from journal entries with mood correlation

    Query params:
        days (int): Number of days to look back (default: 30)
        limit (int): Number of top words to return (default: 50, max: 100)

    Returns word frequency data
    """
    user_id = int(get_jwt_identity())
    days = request.args.get('days', 30, type=int)
    limit = min(request.args.get('limit', 50, type=int), 100)

    start_date = datetime.utcnow() - timedelta(days=days)

    # Get entries
    entries = JournalEntry.query.filter(
        JournalEntry.user_id == user_id,
        JournalEntry.is_deleted == False,
        JournalEntry.formatted_content.isnot(None),
        JournalEntry.created_at >= start_date
    ).all()

    # Extract and count words
    all_words = []
    word_moods = {}  # Track moods when each word appears

    for entry in entries:
        if entry.formatted_content:
            # Extract words (lowercase, alphanumeric only)
            words = re.findall(r'\b[a-z]{3,}\b', entry.formatted_content.lower())

            # Filter stopwords
            words = [w for w in words if w not in STOPWORDS]

            all_words.extend(words)

            # Track mood correlation
            if entry.mood_score:
                for word in words:
                    if word not in word_moods:
                        word_moods[word] = []
                    word_moods[word].append(entry.mood_score)

    # Count frequencies
    word_counts = Counter(all_words)

    # Format response
    words_data = []
    for word, count in word_counts.most_common(limit):
        avg_mood = None
        if word in word_moods and word_moods[word]:
            avg_mood = round(sum(word_moods[word]) / len(word_moods[word]), 1)

        words_data.append({
            'word': word,
            'count': count,
            'avg_mood_when_mentioned': avg_mood
        })

    return jsonify({
        'words': words_data,
        'total_words': len(all_words),
        'unique_words': len(word_counts)
    }), 200
