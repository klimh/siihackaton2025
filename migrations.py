"""
Database migration script for adding avatar and question functionality.
"""
from app import create_app, db
from app.models import Avatar, Question, UserResponse, User, MoodEntry, Conversation, MoodAnalysis, Report, Task, Activity
from app.questions import initialize_questions
from app.utils import ensure_avatar_dirs, initialize_default_avatars
from sqlalchemy import text
from datetime import datetime

def add_role_field():
    """Add role field to User table."""
    with db.engine.connect() as conn:
        conn.execute(text('''
            ALTER TABLE user ADD COLUMN role VARCHAR(10) NOT NULL DEFAULT 'user'
        '''))
        conn.commit()

def create_admin_user():
    """Create admin user if it doesn't exist."""
    admin = User.query.filter_by(email='admin@gmail.com').first()
    if not admin:
        # Get first avatar
        avatar = Avatar.query.first()
        if not avatar:
            print("Error: No avatars found. Please run initialize_default_avatars first.")
            return
        
        admin = User(
            email='admin@gmail.com',
            name='Admin',
            role='admin',
            avatar_id=avatar.id
        )
        admin.set_password('Admin123')
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully!")
    else:
        print("Admin user already exists.")

def init_db():
    """Initialize the database with tables."""
    db.create_all()
    print("Database tables created.")

def drop_db():
    """Drop all database tables."""
    db.drop_all()
    print("Database tables dropped.")

def migrate():
    """Run database migrations."""
    # Create tables if they don't exist
    db.create_all()
    
    # Add any necessary columns or modifications here
    try:
        # Check if Task table exists
        db.session.execute(text('SELECT 1 FROM task LIMIT 1'))
    except:
        # Create Task table
        db.session.execute(text('''
            CREATE TABLE task (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title VARCHAR(200) NOT NULL,
                date DATE NOT NULL,
                completed BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id)
            )
        '''))
        print("Created Task table")
    
    try:
        # Check if Activity table exists
        db.session.execute(text('SELECT 1 FROM activity LIMIT 1'))
    except:
        # Create Activity table
        db.session.execute(text('''
            CREATE TABLE activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type VARCHAR(20) NOT NULL,
                date DATE NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id)
            )
        '''))
        print("Created Activity table")
    
    db.session.commit()
    print("Database migration completed successfully.")

def upgrade():
    """Run all migrations."""
    app = create_app()
    with app.app_context():
        try:
            # Create all tables if they don't exist
            db.create_all()
            
            # Initialize avatars
            ensure_avatar_dirs(app)
            initialize_default_avatars(app)
            
            # Initialize questions
            initialize_questions()
            
            # Add the Report table
            with db.engine.connect() as conn:
                conn.execute(text('''
                    CREATE TABLE IF NOT EXISTS report (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        filename VARCHAR(255) NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES user (id)
                    )
                '''))
                conn.commit()
            
            # Add role field to User table
            try:
                add_role_field()
                print("Added role field to User table.")
            except Exception as e:
                print(f"Note: Role field might already exist: {str(e)}")
            
            # Create admin user
            create_admin_user()
            
            # Run database migrations
            migrate()
            
            print("Database migration completed successfully!")
            
        except Exception as e:
            print(f"Error during migration: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    upgrade() 