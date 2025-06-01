from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User, UserPreferences
from datetime import datetime, time
import json

bp = Blueprint('user', __name__)

@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """
    Get user profile information
    """
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'user': {
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'display_name': user.display_name,
            'avatar_url': user.avatar_url,
            'timezone': user.timezone,
            'locale': user.locale,
            'subscription_tier': user.subscription_tier,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'is_verified': user.is_verified
        }
    }), 200

@bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    Update user profile information
    """
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # Update allowed profile fields
    if 'display_name' in data:
        user.display_name = data['display_name']
    if 'timezone' in data:
        user.timezone = data['timezone']
    if 'locale' in data:
        user.locale = data['locale']
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Profile updated successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'display_name': user.display_name,
                'avatar_url': user.avatar_url,
                'timezone': user.timezone,
                'locale': user.locale,
                'subscription_tier': user.subscription_tier,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'is_verified': user.is_verified
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating user profile: {str(e)}")
        return jsonify({'error': 'Failed to update profile'}), 500

@bp.route('/preferences', methods=['GET'])
@jwt_required()
def get_preferences():
    """
    Get user preferences
    """
    user_id = int(get_jwt_identity())
    preferences = UserPreferences.query.filter_by(user_id=user_id).first()
    
    if not preferences:
        # Create default preferences
        preferences = UserPreferences(user_id=user_id)
        db.session.add(preferences)
        db.session.commit()
    
    return jsonify({
        'preferences': preferences.to_dict()
    }), 200

@bp.route('/preferences', methods=['PUT'])
@jwt_required()
def update_preferences():
    """
    Update user preferences
    """
    user_id = int(get_jwt_identity())
    preferences = UserPreferences.query.filter_by(user_id=user_id).first()
    
    if not preferences:
        preferences = UserPreferences(user_id=user_id)
        db.session.add(preferences)
    
    data = request.get_json()
    
    # Update allowed preference fields
    if 'custom_ai_instructions' in data:
        preferences.custom_ai_instructions = data['custom_ai_instructions']
    
    if 'goals' in data:
        preferences.goals = data['goals']
    
    if 'reminder_enabled' in data:
        preferences.reminder_enabled = data['reminder_enabled']
    
    if 'reminder_time' in data and data['reminder_time']:
        try:
            # Parse time string (HH:MM format)
            time_obj = datetime.strptime(data['reminder_time'], '%H:%M').time()
            preferences.reminder_time = time_obj
        except ValueError:
            return jsonify({'error': 'Invalid time format. Use HH:MM'}), 400
    
    if 'reminder_days' in data:
        preferences.reminder_days = data['reminder_days']
    
    if 'theme' in data:
        preferences.theme = data['theme']
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Preferences updated successfully',
            'preferences': preferences.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating user preferences: {str(e)}")
        return jsonify({'error': 'Failed to update preferences'}), 500

@bp.route('/preferences/goals', methods=['POST'])
@jwt_required()
def add_goal():
    """
    Add a new goal to user preferences
    """
    user_id = int(get_jwt_identity())
    preferences = UserPreferences.query.filter_by(user_id=user_id).first()
    
    if not preferences:
        preferences = UserPreferences(user_id=user_id)
        db.session.add(preferences)
    
    data = request.get_json()
    goal_text = data.get('text', '').strip()
    
    if not goal_text:
        return jsonify({'error': 'Goal text is required'}), 400
    
    try:
        preferences.add_goal(goal_text)
        db.session.commit()
        return jsonify({
            'message': 'Goal added successfully',
            'goals': preferences.goals or []
        }), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error adding goal: {str(e)}")
        return jsonify({'error': 'Failed to add goal'}), 500

@bp.route('/preferences/goals/<int:goal_id>', methods=['DELETE'])
@jwt_required()
def remove_goal(goal_id):
    """
    Remove a goal from user preferences
    """
    user_id = int(get_jwt_identity())
    preferences = UserPreferences.query.filter_by(user_id=user_id).first()
    
    if not preferences:
        return jsonify({'error': 'Preferences not found'}), 404
    
    try:
        preferences.remove_goal(goal_id)
        db.session.commit()
        return jsonify({
            'message': 'Goal removed successfully',
            'goals': preferences.goals or []
        }), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error removing goal: {str(e)}")
        return jsonify({'error': 'Failed to remove goal'}), 500