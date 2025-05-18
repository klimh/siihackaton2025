from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from config import Config
import os

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()

# Configure login manager
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    
    # Initialize CSRF protection
    csrf = CSRFProtect(app)
    
    # Exempt API routes from CSRF protection
    csrf.exempt(app.route('/api/tasks', methods=['GET', 'POST']))
    csrf.exempt(app.route('/api/tasks/<int:task_id>', methods=['PATCH', 'DELETE']))
    csrf.exempt(app.route('/api/activities', methods=['GET', 'POST']))
    
    with app.app_context():
        # Import routes and models
        from app import routes, models
        from app.routes import ensure_avatar_dirs, initialize_default_avatars
        from app.questions import initialize_questions
        
        # Create database tables
        db.create_all()
        
        # Initialize avatars
        ensure_avatar_dirs()
        initialize_default_avatars()
        
        # Initialize questions
        initialize_questions()
        
        # Register blueprints (for future expansion)
        # app.register_blueprint(auth_bp)  # Future authentication blueprint
        # app.register_blueprint(community_bp)  # Future community blueprint
        
        return app 