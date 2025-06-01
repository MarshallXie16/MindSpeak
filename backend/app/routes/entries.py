from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app.models import db, JournalEntry, UsageTracking, User, UserPreferences
import os
import json
from datetime import datetime, timedelta
from sqlalchemy import func, extract

bp = Blueprint('entries', __name__)

# Allowed audio file extensions
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'webm', 'm4a', 'ogg'}

def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/upload-audio', methods=['POST'])
@jwt_required()
def upload_audio():
    """
    Upload audio file for processing
    Creates a new journal entry with pending status
    """
    user_id = int(get_jwt_identity())
    
    # Check usage limits for free tier
    usage = UsageTracking.get_or_create_current_month(user_id)
    user = db.session.get(User, user_id)
    
    if not usage.can_create_entry(user.subscription_tier):
        return jsonify({
            'error': 'Monthly entry limit reached',
            'remaining_entries': 0,
            'subscription_tier': user.subscription_tier
        }), 403
    
    # Validate file upload
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    file = request.files['audio']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file format'}), 400
    
    # Get duration from form data
    duration = request.form.get('duration', type=float)
    if not duration or duration < 5:
        return jsonify({'error': 'Recording too short'}), 400
    
    if duration > 125:  # Allow 5 seconds buffer
        return jsonify({'error': 'Recording too long (max 2 minutes)'}), 400
    
    # Save audio file
    filename = secure_filename(f"{user_id}_{datetime.utcnow().timestamp()}.webm")
    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], str(user_id))
    os.makedirs(upload_path, exist_ok=True)
    
    file_path = os.path.join(upload_path, filename)
    file.save(file_path)
    
    # Create journal entry with pending status
    entry = JournalEntry(
        user_id=user_id,
        audio_filename=filename,
        title="Processing...",
        processing_status='pending'
    )
    db.session.add(entry)
    
    # Update usage tracking
    usage.increment_usage()
    
    db.session.commit()
    
    # TODO: Trigger async processing task
    # For now, we'll implement synchronous processing in the next endpoint
    
    return jsonify({
        'entry_id': entry.id,
        'status': 'processing',
        'message': 'Audio uploaded successfully'
    }), 201

@bp.route('/<int:entry_id>/process', methods=['POST'])
@jwt_required()
def process_entry(entry_id):
    """
    Process the audio file for a journal entry using AI pipeline
    This endpoint triggers the complete AI processing workflow
    """
    user_id = int(get_jwt_identity())
    
    # Get the entry
    entry = JournalEntry.query.filter_by(id=entry_id, user_id=user_id).first()
    if not entry:
        return jsonify({'error': 'Entry not found'}), 404
    
    if entry.processing_status not in ['pending', 'error']:
        return jsonify({'error': 'Entry already processed or in progress'}), 400
    
    # Start processing
    entry.processing_status = 'processing'
    db.session.commit()
    
    # In a production app, this would be done asynchronously with Celery
    # For now, we'll process synchronously but with proper error handling
    import asyncio
    from app.services.journal_ai_service import get_ai_service
    from app.models import UserPreferences
    
    try:
        # Get user context for AI processing
        user = User.query.get(user_id)
        preferences = user.preferences or UserPreferences(user_id=user_id)
        
        user_context = {
            'custom_ai_instructions': preferences.custom_ai_instructions,
            'goals': preferences.goals or []
        }
        
        # Get audio file path
        audio_file_path = os.path.join(
            current_app.config['UPLOAD_FOLDER'], 
            str(user_id), 
            entry.audio_filename
        )
        
        if not os.path.exists(audio_file_path):
            raise Exception(f"Audio file not found: {audio_file_path}")
        
        # Process with AI service
        ai_service = get_ai_service()
        
        # Run async processing in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Process and get final result
            processing_generator = ai_service.process_audio_entry(audio_file_path, user_context)
            final_result = None
            
            # Iterate through progress updates to get final result
            async def get_final_result():
                async for update in processing_generator:
                    if update['status'] == 'complete':
                        return update['result']
                    elif update['status'] == 'error':
                        raise Exception(update.get('error', 'Unknown processing error'))
                return None
            
            final_result = loop.run_until_complete(get_final_result())
            
            if not final_result:
                raise Exception("Processing completed but no result returned")
            
            # Update entry with AI results
            entry.raw_transcript = final_result['raw_transcript']
            entry.title = final_result['title']
            entry.formatted_content = final_result['formatted_content']
            entry.mood_score = final_result['mood_score']
            # Convert lists to JSON strings for SQLite compatibility
            entry.emotions = json.dumps(final_result['emotions']) if isinstance(final_result['emotions'], list) else final_result['emotions']
            entry.insights = json.dumps(final_result['insights']) if isinstance(final_result['insights'], list) else final_result['insights']
            entry.processing_status = 'completed'
            
            # Update user streak
            preferences = UserPreferences.query.filter_by(user_id=user_id).first()
            if not preferences:
                preferences = UserPreferences(user_id=user_id)
                db.session.add(preferences)
            
            preferences.update_streak(entry.created_at)
            
            db.session.commit()
            
            return jsonify({
                'entry_id': entry.id,
                'status': 'completed',
                'message': 'Processing completed successfully',
                'result': final_result
            }), 200
            
        finally:
            loop.close()
            
    except Exception as e:
        # Update entry status to error
        entry.processing_status = 'error'
        db.session.commit()
        
        current_app.logger.error(f"Entry processing failed for entry {entry_id}: {str(e)}")
        return jsonify({
            'entry_id': entry.id,
            'status': 'error',
            'message': f'Processing failed: {str(e)}'
        }), 500

@bp.route('/<int:entry_id>', methods=['GET'])
@jwt_required()
def get_entry(entry_id):
    """
    Get a specific journal entry by ID
    """
    user_id = int(get_jwt_identity())
    
    entry = JournalEntry.query.filter_by(
        id=entry_id, 
        user_id=user_id, 
        is_deleted=False
    ).first()
    
    if not entry:
        return jsonify({'error': 'Entry not found'}), 404
    
    return jsonify({
        'entry': entry.to_dict(include_content=True)
    }), 200

@bp.route('', methods=['GET'])
@jwt_required()
def get_entries():
    """
    Get paginated list of user's journal entries
    """
    user_id = int(get_jwt_identity())
    
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    
    # Limit the number of entries per page
    limit = min(limit, 100)
    
    # Get entries with pagination
    entries = JournalEntry.get_active_entries(
        user_id=user_id,
        limit=limit,
        offset=(page - 1) * limit
    )
    
    # Get total count for pagination info
    total_count = JournalEntry.query.filter_by(
        user_id=user_id,
        is_deleted=False
    ).count()
    
    return jsonify({
        'entries': [entry.to_dict(include_content=False) for entry in entries],
        'pagination': {
            'page': page,
            'limit': limit,
            'total': total_count,
            'pages': (total_count + limit - 1) // limit
        }
    }), 200

@bp.route('/<int:entry_id>', methods=['PUT'])
@jwt_required()
def update_entry(entry_id):
    """
    Update a journal entry
    """
    user_id = int(get_jwt_identity())
    
    entry = JournalEntry.query.filter_by(
        id=entry_id, 
        user_id=user_id, 
        is_deleted=False
    ).first()
    
    if not entry:
        return jsonify({'error': 'Entry not found'}), 404
    
    data = request.get_json()
    
    # Update allowed fields
    if 'title' in data:
        entry.title = data['title']
    if 'formatted_content' in data:
        entry.formatted_content = data['formatted_content']
    if 'mood_score' in data:
        entry.mood_score = data['mood_score']
    if 'emotions' in data:
        entry.emotions = data['emotions']
    if 'insights' in data:
        entry.insights = data['insights']
    
    entry.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Entry updated successfully',
            'entry': entry.to_dict(include_content=True)
        }), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating entry {entry_id}: {str(e)}")
        return jsonify({'error': 'Failed to update entry'}), 500

@bp.route('/<int:entry_id>', methods=['DELETE'])
@jwt_required()
def delete_entry(entry_id):
    """
    Soft delete a journal entry
    """
    user_id = int(get_jwt_identity())
    
    entry = JournalEntry.query.filter_by(
        id=entry_id, 
        user_id=user_id, 
        is_deleted=False
    ).first()
    
    if not entry:
        return jsonify({'error': 'Entry not found'}), 404
    
    try:
        entry.soft_delete()
        return jsonify({'message': 'Entry deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting entry {entry_id}: {str(e)}")
        return jsonify({'error': 'Failed to delete entry'}), 500

@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """
    Get dashboard statistics for the user
    """
    user_id = int(get_jwt_identity())
    
    # Get total entries count
    total_entries = JournalEntry.query.filter_by(
        user_id=user_id,
        is_deleted=False
    ).count()
    
    # Get this month's entries count
    # Using UTC time to match how entries are stored
    current_month = datetime.utcnow().month
    current_year = datetime.utcnow().year
    this_month_entries = JournalEntry.query.filter(
        JournalEntry.user_id == user_id,
        JournalEntry.is_deleted == False,
        extract('month', JournalEntry.created_at) == current_month,
        extract('year', JournalEntry.created_at) == current_year
    ).count()
    
    # Get average mood score
    avg_mood = db.session.query(func.avg(JournalEntry.mood_score)).filter(
        JournalEntry.user_id == user_id,
        JournalEntry.is_deleted == False,
        JournalEntry.mood_score.isnot(None)
    ).scalar()
    
    # Format mood average
    mood_average = round(avg_mood, 1) if avg_mood else None
    
    # Get or create user preferences for streak
    preferences = UserPreferences.query.filter_by(user_id=user_id).first()
    current_streak = preferences.current_streak if preferences else 0
    
    # Get recent entries (last 5)
    recent_entries = JournalEntry.query.filter_by(
        user_id=user_id,
        is_deleted=False
    ).order_by(JournalEntry.created_at.desc()).limit(5).all()
    
    return jsonify({
        'stats': {
            'total_entries': total_entries,
            'current_streak': current_streak,
            'this_month': this_month_entries,
            'mood_average': mood_average
        },
        'recent_entries': [entry.to_dict(include_content=False) for entry in recent_entries]
    }), 200

@bp.route('/hard-delete-all', methods=['DELETE'])
@jwt_required()
def hard_delete_all_soft_deleted():
    """
    Hard delete all soft deleted entries for the current user
    TODO: Make this admin-only or add additional protection
    """
    user_id = int(get_jwt_identity())
    
    try:
        # Find all soft deleted entries
        soft_deleted_entries = JournalEntry.query.filter_by(
            user_id=user_id,
            is_deleted=True
        ).all()
        
        # Delete audio files for soft deleted entries
        deleted_count = 0
        for entry in soft_deleted_entries:
            if entry.audio_file_path and os.path.exists(entry.audio_file_path):
                try:
                    os.remove(entry.audio_file_path)
                except Exception as e:
                    current_app.logger.warning(f"Could not delete audio file {entry.audio_file_path}: {str(e)}")
            
            db.session.delete(entry)
            deleted_count += 1
        
        db.session.commit()
        
        return jsonify({
            'message': f'Successfully hard deleted {deleted_count} entries',
            'deleted_count': deleted_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error hard deleting entries: {str(e)}")
        return jsonify({'error': 'Failed to hard delete entries'}), 500

@bp.route('/trash', methods=['GET'])
@jwt_required()
def get_trash():
    """
    Get all soft deleted entries for the current user
    """
    user_id = int(get_jwt_identity())
    
    # Get soft deleted entries
    soft_deleted_entries = JournalEntry.query.filter_by(
        user_id=user_id,
        is_deleted=True
    ).order_by(JournalEntry.updated_at.desc()).all()
    
    return jsonify({
        'entries': [entry.to_dict(include_content=False) for entry in soft_deleted_entries],
        'count': len(soft_deleted_entries)
    }), 200

@bp.route('/fix-streaks', methods=['POST'])
@jwt_required()
def fix_user_streaks():
    """
    Fix streak tracking for existing entries
    This recalculates the streak based on all completed entries
    """
    user_id = int(get_jwt_identity())
    
    try:
        # Get or create preferences
        preferences = UserPreferences.query.filter_by(user_id=user_id).first()
        if not preferences:
            preferences = UserPreferences(user_id=user_id)
            db.session.add(preferences)
        
        # Reset streak counters
        preferences.current_streak = 0
        preferences.longest_streak = 0
        preferences.last_entry_date = None
        
        # Get all completed entries ordered by date
        entries = JournalEntry.query.filter(
            JournalEntry.user_id == user_id,
            JournalEntry.is_deleted == False,
            JournalEntry.processing_status == 'completed'
        ).order_by(JournalEntry.created_at.asc()).all()
        
        # Recalculate streak for each entry
        for entry in entries:
            preferences.update_streak(entry.created_at)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Streak recalculated successfully',
            'current_streak': preferences.current_streak,
            'longest_streak': preferences.longest_streak,
            'total_entries': len(entries)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error fixing streaks: {str(e)}")
        return jsonify({'error': 'Failed to fix streaks'}), 500