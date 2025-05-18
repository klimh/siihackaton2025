from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager
from enum import Enum
import numpy as np
import os

class ActivityType(str, Enum):
    MEDITATION = 'meditation'
    STEPS = 'steps'
    BREATHING = 'breathing'

class SenderType(str, Enum):
    USER = 'user'
    AI = 'ai'

class Avatar(db.Model):
    """Avatar model for user profile pictures."""
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    users = db.relationship('User', backref='avatar', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename
        }

class User(UserMixin, db.Model):
    """User model for authentication and profile data."""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    avatar_id = db.Column(db.Integer, db.ForeignKey('avatar.id'))
    role = db.Column(db.String(10), nullable=False, default='user')  # 'user' or 'admin'
    
    # Relationships
    mood_entries = db.relationship('MoodEntry', backref='user', lazy=True)
    conversations = db.relationship('Conversation', backref='user', lazy=True)
    responses = db.relationship('UserResponse', backref='user', lazy=True)
    tasks = db.relationship('Task', back_populates='user', lazy=True)
    activities = db.relationship('Activity', back_populates='user', lazy=True)
    help_accesses = db.relationship('HelpAccess', backref='user', lazy=True)
    surveys = db.relationship('Survey', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def calculate_mood_stats(self):
        """Calculate average mood and mood deviation."""
        from sqlalchemy import func
        from app import db
        
        result = db.session.query(
            func.avg(MoodEntry.mood_score).label('average'),
            func.stddev(MoodEntry.mood_score).label('deviation')
        ).filter(MoodEntry.user_id == self.id).first()
        
        return result.average or 0, result.deviation or 0

    def calculate_recent_mood_average(self):
        """Calculate average mood for the last 7 days."""
        from sqlalchemy import func
        from datetime import datetime, timedelta
        
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        result = db.session.query(
            func.avg(MoodEntry.mood_score).label('average')
        ).filter(
            MoodEntry.user_id == self.id,
            MoodEntry.timestamp >= seven_days_ago
        ).first()
        
        return float(result.average) if result.average else None

    def is_admin(self):
        """Check if user is an admin."""
        return self.role == 'admin'

    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'role': self.role,
            'avatar': self.avatar.to_dict() if self.avatar else None,
            'task_count': len(self.tasks),
            'activity_count': len(self.activities),
            'help_access_count': len(self.help_accesses)
        }

class MoodEntry(db.Model):
    """Model for tracking user mood entries."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mood_score = db.Column(db.Integer, nullable=False)  # 1-10 scale
    note = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'mood_score': self.mood_score,
            'note': self.note,
            'timestamp': self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data, user_id):
        return cls(
            user_id=user_id,
            mood_score=data['mood_score'],
            note=data.get('note', '')
        )

class Conversation(db.Model):
    """Model for storing chat messages."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    sender = db.Column(db.String(10), nullable=False)  # 'user' or 'ai'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    sentiment_score = db.Column(db.Float)  # -1 to 1 scale

    def to_dict(self):
        return {
            'id': self.id,
            'message': self.message,
            'sender': self.sender,
            'timestamp': self.timestamp.isoformat(),
            'sentiment_score': self.sentiment_score
        }

class MoodAnalysis(db.Model):
    """Model for storing mood analysis results."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    average_mood = db.Column(db.Float, nullable=False)
    mood_deviation = db.Column(db.Float, nullable=False)
    analysis_timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'average_mood': self.average_mood,
            'mood_deviation': self.mood_deviation,
            'analysis_timestamp': self.analysis_timestamp.isoformat()
        }

    @classmethod
    def from_stats(cls, user_id, average_mood, mood_deviation):
        return cls(
            user_id=user_id,
            average_mood=average_mood,
            mood_deviation=mood_deviation
        )

class Question(db.Model):
    """Model for daily reflection questions."""
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    responses = db.relationship('UserResponse', backref='question', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text
        }

class UserResponse(db.Model):
    """Model for storing user responses to daily questions."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    mood_entry_id = db.Column(db.Integer, db.ForeignKey('mood_entry.id'))

    def to_dict(self):
        return {
            'id': self.id,
            'question': self.question.text,
            'response': self.response,
            'timestamp': self.timestamp.isoformat()
        }

class Report(db.Model):
    """Model for storing generated PDF reports."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with User model
    user = db.relationship('User', backref=db.backref('reports', lazy=True))
    
    def get_file_path(self):
        """Get the full path to the report file."""
        return os.path.join('static', 'reports', self.filename)
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'created_at': self.created_at.isoformat(),
            'download_url': f'/report/download/{self.filename}'
        }

class Task(db.Model):
    """Model for user tasks."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship with User model
    user = db.relationship('User', back_populates='tasks')

    def to_dict(self):
        """Convert task to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'date': self.date.isoformat(),
            'completed': self.completed,
            'created_at': self.created_at.isoformat()
        }

class Activity(db.Model):
    """Model for completed activities."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # meditation, steps, breathing
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship with User model
    user = db.relationship('User', back_populates='activities')

    @property
    def color(self):
        """Get the color associated with the activity type."""
        color_map = {
            'meditation': 'green',
            'steps': 'blue',
            'breathing': 'purple'
        }
        return color_map.get(self.type, 'gray')

    def to_dict(self):
        """Convert activity to dictionary."""
        return {
            'id': self.id,
            'type': self.type,
            'date': self.date.isoformat(),
            'color': self.color,
            'created_at': self.created_at.isoformat()
        }

class HelpAccess(db.Model):
    """Model for tracking help page visits."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert help access to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'timestamp': self.timestamp.isoformat()
        }

class Survey(db.Model):
    """Model for daily user surveys."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    activities = db.Column(db.Text, nullable=False)  # JSON-encoded list of activity IDs
    custom_activities = db.Column(db.Text)  # JSON-encoded list of custom activities
    social_media_time = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'date', name='uix_user_date'),
    )

    def set_activities(self, activities):
        """Set activities as JSON-encoded list."""
        import json
        self.activities = json.dumps(activities)

    def get_activities(self):
        """Get activities as Python list."""
        import json
        return json.loads(self.activities) if self.activities else []

    def set_custom_activities(self, custom_activities):
        """Set custom activities as JSON-encoded list."""
        import json
        if custom_activities:
            self.custom_activities = json.dumps(custom_activities)
        else:
            self.custom_activities = None

    def get_custom_activities(self):
        """Get custom activities as Python list."""
        import json
        return json.loads(self.custom_activities) if self.custom_activities else []

    def to_dict(self):
        """Convert survey to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat(),
            'activities': self.get_activities(),
            'custom_activities': self.get_custom_activities(),
            'social_media_time': self.social_media_time,
            'created_at': self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data, user_id):
        """Create Survey instance from dictionary data."""
        from datetime import datetime
        survey = cls(
            user_id=user_id,
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            social_media_time=data['social_media_time']
        )
        survey.set_activities(data['activities'])
        if 'custom_activities' in data:
            survey.set_custom_activities(data['custom_activities'])
        return survey

    def get_activity_details(self):
        """Get detailed activity information."""
        from app.survey_config import get_activity_by_id
        activities = self.get_activities()
        return [get_activity_by_id(activity_id) for activity_id in activities]

    def get_social_media_details(self):
        """Get detailed social media time information."""
        from app.survey_config import get_social_media_option
        return get_social_media_option(self.social_media_time)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id)) 