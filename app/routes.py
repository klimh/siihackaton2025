from flask import current_app as app, jsonify, request, render_template, redirect, url_for, flash, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import MoodEntry, User, Conversation, MoodAnalysis, Avatar, Question, UserResponse, Report, Task, Activity, HelpAccess, Survey
from app.chatbot import ChatBot
from app.questions import initialize_questions, get_random_question, save_response
from app.decorators import admin_required
from urllib.parse import urlparse
from datetime import datetime, timedelta
import os
import hashlib
from PIL import Image, ImageDraw
from app.report_generator import ReportGenerator
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()

def generate_identicon(text, size=420):
    """Generate an identicon-style avatar."""
    # Create a hash of the text
    hash_object = hashlib.md5(text.encode())
    hash_hex = hash_object.hexdigest()
    
    # Create a new image with a white background
    image = Image.new('RGB', (size, size), 'white')
    draw = ImageDraw.Draw(image)
    
    # Use the hash to determine the color
    color = '#{}'.format(hash_hex[:6])
    
    # Create a 5x5 grid of squares
    block_size = size // 5
    for i in range(3):  # Only need to do half, will mirror
        for j in range(5):
            if int(hash_hex[i * 5 + j], 16) % 2 == 0:  # Use hash to determine if block should be filled
                # Draw the square and its mirror
                draw.rectangle([
                    i * block_size, j * block_size,
                    (i + 1) * block_size - 1, (j + 1) * block_size - 1
                ], fill=color)
                # Mirror the square
                draw.rectangle([
                    (4 - i) * block_size, j * block_size,
                    (5 - i) * block_size - 1, (j + 1) * block_size - 1
                ], fill=color)
    
    return image

# Ensure avatar directories exist
def ensure_avatar_dirs():
    """Ensure avatar directories exist and create them if they don't."""
    avatar_dir = os.path.join(app.static_folder, 'avatars')
    custom_dir = os.path.join(avatar_dir, 'custom')
    os.makedirs(avatar_dir, exist_ok=True)
    os.makedirs(custom_dir, exist_ok=True)
    
    # Create default avatar
    default_path = os.path.join(avatar_dir, 'default.png')
    if not os.path.exists(default_path):
        default_avatar = generate_identicon('default')
        default_avatar.save(default_path, 'PNG')

# Initialize default avatars
def initialize_default_avatars():
    """Initialize default avatars if they don't exist."""
    if Avatar.query.count() == 0:
        avatar_dir = os.path.join(app.static_folder, 'avatars')
        
        # Create default avatars with different seeds
        for i in range(1, 11):
            filename = f'avatar{i}.png'
            filepath = os.path.join(avatar_dir, filename)
            
            if not os.path.exists(filepath):
                avatar = generate_identicon(f'avatar{i}')
                avatar.save(filepath, 'PNG')
            
            db_avatar = Avatar(filename=filename, is_custom=False)
            db.session.add(db_avatar)
        
        db.session.commit()

# Authentication Routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        data = request.form
        if User.query.filter_by(email=data['email']).first():
            flash('Email already registered')
            return redirect(url_for('register'))
        
        # Handle avatar selection
        avatar_id = data.get('avatar_id')
        if not avatar_id:
            flash('Please select an avatar')
            return redirect(url_for('register'))
        
        # Create user with selected avatar
        user = User(
            email=data['email'],
            name=data['name'],
            avatar_id=avatar_id
        )
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin_panel'))
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user is None or not user.check_password(request.form['password']):
            flash('Invalid email or password')
            return redirect(url_for('login'))
        
        login_user(user)
        
        # Redirect admin users to admin panel
        if user.is_admin():
            return redirect(url_for('admin_panel'))
            
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/profile/report', methods=['GET'])
@login_required
def generate_report():
    """Generate a PDF report for the current user."""
    try:
        generator = ReportGenerator(current_user)
        report = generator.generate_report()
        
        return jsonify({
            'status': 'success',
            'report': report.to_dict()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/admin')
@login_required
@admin_required
def admin_panel():
    """Admin panel showing all users and their reports."""
    users = User.query.all()
    return render_template('admin.html', users=users)

@app.route('/admin/report/download/<filename>')
@login_required
@admin_required
def admin_download_report(filename):
    """Download a report file (admin access)."""
    reports_dir = os.path.join(app.root_path, 'static', 'reports')
    return send_from_directory(reports_dir, filename, as_attachment=True)

@app.route('/report/download/<filename>')
@login_required
def download_report(filename):
    """Download a report file (user access)."""
    # Security check: ensure the report belongs to the current user
    report = Report.query.filter_by(filename=filename, user_id=current_user.id).first_or_404()
    
    reports_dir = os.path.join(app.root_path, 'static', 'reports')
    return send_from_directory(reports_dir, filename, as_attachment=True)

# Page Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mood-journal')
@login_required
def mood_journal():
    return render_template('mood_journal.html')

@app.route('/relaxation')
@login_required
def relaxation():
    return render_template('relaxation.html')

@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html')

# API Routes
@app.route('/api/mood', methods=['POST'])
@login_required
def create_mood():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        if 'mood_score' not in data:
            return jsonify({'error': 'Missing mood_score'}), 400
        
        try:
            mood_score = int(data['mood_score'])
            if not (1 <= mood_score <= 10):
                return jsonify({'error': 'Mood score must be between 1 and 10'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid mood score format'}), 400
        
        mood_entry = MoodEntry.from_dict(data, current_user.id)
        db.session.add(mood_entry)
        db.session.commit()
        
        return jsonify(mood_entry.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error creating mood entry: {str(e)}')
        return jsonify({'error': 'Failed to save mood entry. Please try again.'}), 500

@app.route('/api/moods')
@login_required
def get_moods():
    try:
        entries = MoodEntry.query.filter_by(user_id=current_user.id).order_by(MoodEntry.timestamp.desc()).all()
        return jsonify([entry.to_dict() for entry in entries])
    except Exception as e:
        app.logger.error(f'Error fetching mood entries: {str(e)}')
        return jsonify({'error': 'Failed to fetch mood entries'}), 500

@app.route('/api/mood/<int:id>')
@login_required
def get_mood(id):
    try:
        entry = MoodEntry.query.filter_by(id=id, user_id=current_user.id).first_or_404()
        return jsonify(entry.to_dict())
    except Exception as e:
        app.logger.error(f'Error fetching mood entry {id}: {str(e)}')
        return jsonify({'error': 'Failed to fetch mood entry'}), 500

@app.route('/api/test-chat')
@login_required
def test_chat_connection():
    """Test the connection to the Gemini API."""
    success, message = ChatBot.test_api_connection()
    return jsonify({
        'success': success,
        'message': message
    })

@app.route('/api/chat', methods=['POST'])
@login_required
def process_chat():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400

        if not data['message'].strip():
            return jsonify({'error': 'Message cannot be empty'}), 400

        # Process message through chatbot
        response = ChatBot.process_message(data['message'], current_user.id)
        
        if 'error' in response:
            return jsonify({'error': response['error']}), 500
            
        return jsonify(response)

    except Exception as e:
        app.logger.error(f'Error processing chat message: {str(e)}')
        return jsonify({'error': 'An unexpected error occurred. Please try again.'}), 500

@app.route('/api/chat/history')
@login_required
def get_chat_history():
    try:
        # Get last 50 messages
        messages = Conversation.query.filter_by(user_id=current_user.id)\
            .order_by(Conversation.timestamp.desc())\
            .limit(50)\
            .all()
        
        return jsonify([msg.to_dict() for msg in messages[::-1]])  # Reverse to get chronological order

    except Exception as e:
        app.logger.error(f'Error fetching chat history: {str(e)}')
        return jsonify({'error': 'Failed to fetch chat history'}), 500

@app.route('/api/mood_analysis')
@login_required
def get_mood_analysis():
    try:
        # Get latest mood analysis
        analysis = ChatBot.get_mood_analysis(current_user.id)
        
        # Get current sentiment (average of last 5 messages)
        recent_messages = Conversation.query.filter_by(
            user_id=current_user.id,
            sender='user'  # Only user messages have sentiment
        ).order_by(Conversation.timestamp.desc()).limit(5).all()
        
        current_sentiment = None
        if recent_messages:
            sentiments = [msg.sentiment_score for msg in recent_messages if msg.sentiment_score is not None]
            if sentiments:
                current_sentiment = sum(sentiments) / len(sentiments)
        
        analysis['current_sentiment'] = current_sentiment
        return jsonify(analysis)

    except Exception as e:
        app.logger.error(f'Error fetching mood analysis: {str(e)}')
        return jsonify({'error': 'Failed to fetch mood analysis'}), 500

# Placeholder routes for future features
@app.route('/habits')
@login_required
def habits():
    return jsonify({'message': 'Habits feature coming soon!'})

@app.route('/community')
@login_required
def community():
    return jsonify({'message': 'Community feature coming soon!'})

# Password reset placeholder
# @app.route('/reset_password_request', methods=['GET', 'POST'])
# def reset_password_request():
#     pass

# @app.route('/reset_password/<token>', methods=['GET', 'POST'])
# def reset_password(token):
#     pass 

# Avatar Routes
@app.route('/api/avatars')
@login_required
def get_avatars():
    """Get list of available avatars."""
    avatars = Avatar.query.all()
    return jsonify([avatar.to_dict() for avatar in avatars])

@app.route('/api/user/avatar')
@login_required
def get_user_avatar():
    """Get current user's avatar details."""
    if not current_user.avatar:
        return jsonify({'error': 'No avatar found'}), 404
    return jsonify(current_user.avatar.to_dict())

# Question Routes
@app.route('/api/random_question')
@login_required
def random_question():
    """Get a random unanswered question for today."""
    question = get_random_question(current_user.id)
    if not question:
        return jsonify({'message': 'No more questions for today'}), 404
    return jsonify(question.to_dict())

@app.route('/api/answer_question', methods=['POST'])
@login_required
def answer_question():
    """Save user's response to a question."""
    data = request.get_json()
    if not data or 'question_id' not in data or 'response' not in data:
        return jsonify({'error': 'Invalid request data'}), 400
    
    try:
        response = save_response(
            user_id=current_user.id,
            question_id=data['question_id'],
            response_text=data['response']
        )
        return jsonify({'message': 'Response saved successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/calendar')
@login_required
def calendar():
    """Calendar view for tasks and activities."""
    return render_template('calendar.html')

@app.route('/api/tasks', methods=['GET', 'POST'])
@login_required
def handle_tasks():
    """Handle task creation and retrieval."""
    if request.method == 'POST':
        data = request.json
        task = Task(
            user_id=current_user.id,
            title=data['title'],
            date=datetime.strptime(data['date'], '%Y-%m-%d').date()
        )
        db.session.add(task)
        db.session.commit()
        return jsonify(task.to_dict())
    else:
        # Get tasks for the specified month and year
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        
        if month and year:
            start_date = datetime(year, month, 1).date()
            if month == 12:
                end_date = datetime(year + 1, 1, 1).date()
            else:
                end_date = datetime(year, month + 1, 1).date()
            
            tasks = Task.query.filter(
                Task.user_id == current_user.id,
                Task.date >= start_date,
                Task.date < end_date
            ).order_by(Task.date).all()
        else:
            tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.date).all()
        
        return jsonify([task.to_dict() for task in tasks])

@app.route('/api/tasks/<int:task_id>', methods=['PATCH', 'DELETE'])
@login_required
def handle_task(task_id):
    """Handle task updates and deletion."""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    
    if request.method == 'PATCH':
        data = request.json
        if 'completed' in data:
            task.completed = data['completed']
        if 'title' in data:
            task.title = data['title']
        if 'date' in data:
            task.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        db.session.commit()
        return jsonify(task.to_dict())
    
    elif request.method == 'DELETE':
        db.session.delete(task)
        db.session.commit()
        return '', 204

@app.route('/api/activities', methods=['GET', 'POST'])
@login_required
def handle_activities():
    """Handle activity logging and retrieval."""
    if request.method == 'POST':
        data = request.json
        activity = Activity(
            user_id=current_user.id,
            type=data['type'],
            date=datetime.strptime(data['date'], '%Y-%m-%d').date()
        )
        db.session.add(activity)
        db.session.commit()
        return jsonify(activity.to_dict())
    else:
        # Get activities for the specified month and year
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        
        if month and year:
            start_date = datetime(year, month, 1).date()
            if month == 12:
                end_date = datetime(year + 1, 1, 1).date()
            else:
                end_date = datetime(year, month + 1, 1).date()
            
            activities = Activity.query.filter(
                Activity.user_id == current_user.id,
                Activity.date >= start_date,
                Activity.date < end_date
            ).order_by(Activity.date).all()
        else:
            activities = Activity.query.filter_by(user_id=current_user.id).order_by(Activity.date).all()
        
        return jsonify([activity.to_dict() for activity in activities])

@app.route('/help')
@login_required
def help_page():
    """Render the help page with emergency and other contacts."""
    from app.help_contacts import get_emergency_contacts, get_contacts_by_category
    
    # Track the help page access
    help_access = HelpAccess(user_id=current_user.id)
    db.session.add(help_access)
    db.session.commit()
    
    # Get emergency and other contacts
    emergency_contacts = get_emergency_contacts()
    other_contacts = [c for c in get_contacts_by_category() if c['category'] != 'emergency']
    
    # Get user's recent mood average for contextual styling
    recent_mood = current_user.calculate_recent_mood_average()
    
    return render_template(
        'help.html',
        emergency_contacts=emergency_contacts,
        other_contacts=other_contacts,
        recent_mood=recent_mood
    )

@app.route('/survey')
@login_required
def survey_page():
    """Render the daily survey page."""
    from datetime import datetime
    from app.survey_config import ACTIVITY_OPTIONS, SOCIAL_MEDIA_OPTIONS
    
    return render_template(
        'survey.html',
        activity_options=ACTIVITY_OPTIONS,
        social_media_options=SOCIAL_MEDIA_OPTIONS,
        today=datetime.utcnow()
    )

@app.route('/api/survey', methods=['POST'])
@login_required
def create_survey():
    """Create or update a daily survey."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        required_fields = ['date', 'activities', 'social_media_time']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Validate activities and social media time
        from app.survey_config import validate_activities, validate_social_media_time
        
        if not validate_activities(data['activities']):
            return jsonify({'error': 'Invalid activities'}), 400
            
        if not validate_social_media_time(data['social_media_time']):
            return jsonify({'error': 'Invalid social media time'}), 400
            
        # Check if survey already exists for this date
        from datetime import datetime
        survey_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        existing_survey = Survey.query.filter_by(
            user_id=current_user.id,
            date=survey_date
        ).first()
        
        if existing_survey:
            # Update existing survey
            existing_survey.set_activities(data['activities'])
            if 'custom_activities' in data:
                existing_survey.set_custom_activities(data['custom_activities'])
            existing_survey.social_media_time = data['social_media_time']
            survey = existing_survey
        else:
            # Create new survey
            survey = Survey.from_dict(data, current_user.id)
            db.session.add(survey)
            
        db.session.commit()
        return jsonify(survey.to_dict()), 200 if existing_survey else 201
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error creating survey: {str(e)}')
        return jsonify({'error': 'Failed to save survey. Please try again.'}), 500

@app.route('/api/survey/<date>')
@login_required
def get_survey(date):
    """Get survey for a specific date."""
    try:
        from datetime import datetime
        survey_date = datetime.strptime(date, '%Y-%m-%d').date()
        survey = Survey.query.filter_by(
            user_id=current_user.id,
            date=survey_date
        ).first()
        
        if not survey:
            return jsonify({'error': 'Survey not found'}), 404
            
        return jsonify(survey.to_dict())
        
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    except Exception as e:
        app.logger.error(f'Error fetching survey: {str(e)}')
        return jsonify({'error': 'Failed to fetch survey'}), 500

@app.route('/api/survey/stats')
@login_required
def get_survey_stats():
    """Get survey statistics for the current user."""
    try:
        from sqlalchemy import func
        from datetime import datetime, timedelta
        
        # Get total surveys count
        total_surveys = Survey.query.filter_by(user_id=current_user.id).count()
        
        # Get surveys in the last 30 days
        thirty_days_ago = datetime.utcnow().date() - timedelta(days=30)
        recent_surveys = Survey.query.filter(
            Survey.user_id == current_user.id,
            Survey.date >= thirty_days_ago
        ).count()
        
        return jsonify({
            'total_surveys': total_surveys,
            'recent_surveys': recent_surveys
        })
        
    except Exception as e:
        app.logger.error(f'Error fetching survey stats: {str(e)}')
        return jsonify({'error': 'Failed to fetch survey statistics'}), 500

@app.route('/api/help/stats')
@login_required
def help_stats():
    """Get help page access statistics for the current user."""
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    # Get total help page accesses
    total_accesses = HelpAccess.query.filter_by(user_id=current_user.id).count()
    
    # Get help page accesses in the last 7 days
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_accesses = HelpAccess.query.filter(
        HelpAccess.user_id == current_user.id,
        HelpAccess.timestamp >= seven_days_ago
    ).count()
    
    return jsonify({
        'total_accesses': total_accesses,
        'recent_accesses': recent_accesses
    }) 