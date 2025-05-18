from textblob import TextBlob
from app.models import Conversation, MoodAnalysis, SenderType
from app import db
from datetime import datetime, timedelta
import os
import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class ChatBot:
    """Chatbot using Google's Gemini AI with sentiment analysis."""

    # Gemini API configuration
    API_KEY = "AIzaSyDCdotWUzy8s7m0zA5guE5ptINu0oSMvqI"
    API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent" # Using gemini-2.0-flash as per your code

    # System prompt for mental health support
    SYSTEM_PROMPT = """You are a supportive mental health chatbot. Your role is to:
    1. Provide empathetic and understanding responses
    2. Offer constructive suggestions when appropriate
    3. Encourage positive thinking and healthy coping mechanisms
    4. Recognize when to suggest professional help
    5. Maintain a supportive and non-judgmental tone
    Remember: You are not a replacement for professional mental health care.
    Always encourage seeking professional help for serious concerns."""

    # Configure max response tokens
    MAX_RESPONSE_TOKENS = 150 # You can adjust this number

    @staticmethod
    def analyze_sentiment(text):
        """Analyze the sentiment of a message using TextBlob."""
        try:
            blob = TextBlob(text)
            return blob.sentiment.polarity  # Returns value between -1 and 1
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return 0

    @classmethod
    def get_ai_response(cls, message, context=None):
        """Get response from Gemini AI using direct API call."""
        if not cls.API_KEY:
            logger.error("API key not configured")
            return "I apologize, but I'm currently unable to process messages. API key not configured."

        try:
            # Prepare the message
            data = {
                "contents": [
                    {
                        "parts": [
                            {"text": cls.SYSTEM_PROMPT},
                            # Consider adding context here if needed for more complex conversations
                            {"text": message}
                        ]
                    }
                ],
                "generationConfig": { # Add generation configuration
                    "max_output_tokens": cls.MAX_RESPONSE_TOKENS
                    # You can add other parameters here like temperature, top_p, top_k if needed
                }
            }

            # Make the API call
            logger.debug(f"Sending API request: {json.dumps(data, indent=2)}")
            response = requests.post(
                f"{cls.API_URL}?key={cls.API_KEY}",
                headers={'Content-Type': 'application/json'},
                json=data,
                timeout=10
            )

            # Check if the request was successful
            response.raise_for_status()
            response_data = response.json()
            logger.debug(f"API response: {json.dumps(response_data, indent=2)}")

            if 'candidates' in response_data and len(response_data['candidates']) > 0:
                 # Check if the response has content parts
                if 'content' in response_data['candidates'][0] and 'parts' in response_data['candidates'][0]['content'] and len(response_data['candidates'][0]['content']['parts']) > 0:
                    return response_data['candidates'][0]['content']['parts'][0]['text']
                else:
                     logger.warning(f"Response received but no text content: {response_data}")
                     return "I received a response, but it didn't contain a text message."


            logger.error(f"No candidates in response: {response_data}")
            # Check for prompt feedback or block reasons
            if 'promptFeedback' in response_data:
                 logger.error(f"Prompt feedback: {response_data['promptFeedback']}")
                 return "I'm sorry, I couldn't generate a response to that message."


            return "I apologize, but I'm having trouble processing your message. Please try again."

        except requests.exceptions.RequestException as e:
            logger.error(f"API request error: {e}")
            return "I apologize, but I'm having trouble connecting to the AI service. Please try again later."
        except (KeyError, IndexError) as e:
            logger.error(f"Response parsing error: {e}")
            return "I apologize, but the AI response was invalid. Please try again."
        except Exception as e:
            logger.error(f"Unexpected error in get_ai_response: {e}")
            return "I apologize, but I'm having trouble processing your message. Please try again."

    @classmethod
    def process_message(cls, message, user_id):
        """Process a user message and return an AI response."""
        try:
            # Get recent context - Note: Your current API call does *not* use this context.
            # To use context, you'd need to include the 'recent_messages'
            # in the 'contents' list of the API request, potentially structured
            # as back-and-forth turns.
            context = cls.get_recent_context(user_id) # This is fetched but not used in get_ai_response
            # Example of how context might be included (more complex):
            # You'd restructure 'data' in get_ai_response to build a conversation history
            # data = {"contents": [{"parts": [{"text": cls.SYSTEM_PROMPT}]}] +
            #                     [{"role": "user" if msg.sender == SenderType.USER else "model", "parts": [{"text": msg.message}]} for msg in context] +
            #                     [{"role": "user", "parts": [{"text": message}]}],
            #         "generationConfig": {"max_output_tokens": cls.MAX_RESPONSE_TOKENS}}


            # Get sentiment score
            sentiment_score = cls.analyze_sentiment(message)
            logger.debug(f"Sentiment score for message '{message}': {sentiment_score}")

            # Get AI response
            # Call get_ai_response without passing context for now, as it's not used
            response = cls.get_ai_response(message)
            logger.debug(f"AI response: {response}")

            # Save user message
            user_message = Conversation(
                message=message,
                sender=SenderType.USER,
                sentiment_score=sentiment_score,
                user_id=user_id
            )
            db.session.add(user_message)

            # Save AI response
            ai_message = Conversation(
                message=response,
                sender=SenderType.AI,
                sentiment_score=None,  # AI responses don't have sentiment
                user_id=user_id
            )
            db.session.add(ai_message)

            # Update mood analysis
            try:
                cls.update_mood_analysis(user_id)
            except Exception as e:
                logger.error(f"Error updating mood analysis: {e}")

            db.session.commit()
            logger.info(f"Successfully processed message for user {user_id}")

            return {
                'message': response,
                'sentiment_score': sentiment_score
            }

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            db.session.rollback()
            return {
                'message': "I apologize, but I'm having temporary difficulties. Please try again.",
                'sentiment_score': 0
            }

    @staticmethod
    def get_recent_context(user_id, limit=5):
        """Get recent conversation context for a user."""
        try:
            # Make sure Conversation model has a timestamp column
            recent_messages = Conversation.query.filter_by(user_id=user_id) \
                .order_by(Conversation.timestamp.desc()) \
                .limit(limit) \
                .all()
            return recent_messages[::-1]  # Reverse to get chronological order
        except Exception as e:
            logger.error(f"Error getting recent context: {e}")
            return []

    @staticmethod
    def update_mood_analysis(user_id):
        """Update mood analysis for a user."""
        try:
            from app.models import User
            user = User.query.get(user_id)
            if not user:
                logger.error(f"User {user_id} not found")
                return

            # Calculate mood statistics
            # Ensure User model has calculate_mood_stats method
            average_mood, mood_deviation = user.calculate_mood_stats()

            # Create new mood analysis entry
            # Ensure MoodAnalysis model has from_stats class method
            analysis = MoodAnalysis.from_stats(user_id, average_mood, mood_deviation)
            db.session.add(analysis)
        except Exception as e:
            logger.error(f"Error in update_mood_analysis: {e}")