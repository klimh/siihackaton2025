"""
Questions module for the mental health support app.
Contains predefined questions and helper functions for question management.
"""
from datetime import datetime, timedelta
from random import choice
from app.models import Question, UserResponse
from app import db

# Predefined questions for daily reflection
QUESTIONS = [
    "How are you feeling today?",
    "What made you smile today?",
    "What's one thing you're grateful for today?",
    "What's something you're looking forward to?",
    "How did you take care of yourself today?",
    "What was the most challenging part of your day?",
    "What's one thing you learned today?",
    "How did you connect with others today?",
    "What's one goal you have for tomorrow?",
    "What's something that brought you peace today?",
    "How would you rate your energy level today?",
    "What's one thing you'd like to improve?",
    "Who made a positive impact on your day?",
    "What's a small win you had today?",
    "How did you handle stress today?",
    "What's one thing you're proud of?",
    "How well did you sleep last night?",
    "What's one thing you could have done differently today?",
    "What's a positive thought you had today?",
    "How would you describe your mood in one word?"
]

def initialize_questions():
    """Initialize the questions table with predefined questions."""
    existing_count = Question.query.count()
    if existing_count == 0:
        for text in QUESTIONS:
            question = Question(text=text)
            db.session.add(question)
        db.session.commit()

def get_random_question(user_id):
    """
    Get a random question for the user that hasn't been answered today.
    Returns None if all questions have been answered today.
    """
    today = datetime.utcnow().date()
    tomorrow = today + timedelta(days=1)
    
    # Get questions answered today
    answered_today = UserResponse.query.filter(
        UserResponse.user_id == user_id,
        UserResponse.timestamp >= today,
        UserResponse.timestamp < tomorrow
    ).with_entities(UserResponse.question_id).all()
    
    answered_ids = [q[0] for q in answered_today]
    
    # Get available questions
    available_questions = Question.query.filter(
        ~Question.id.in_(answered_ids) if answered_ids else True
    ).all()
    
    return choice(available_questions) if available_questions else None

def save_response(user_id, question_id, response_text):
    """Save a user's response to a question."""
    user_response = UserResponse(
        user_id=user_id,
        question_id=question_id,
        response=response_text,
        timestamp=datetime.utcnow()
    )
    db.session.add(user_response)
    db.session.commit()
    return user_response 