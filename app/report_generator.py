import os
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
from app.models import MoodEntry, Conversation, UserResponse, Report, Survey
from app import db
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path
from collections import Counter
from app.survey_config import ACTIVITY_OPTIONS, SOCIAL_MEDIA_OPTIONS, ACTIVITY_CATEGORIES, get_activity_by_id

class ReportGenerator:
    def __init__(self, user):
        self.user = user
        self.report_dir = os.path.join('app', 'static', 'reports')
        os.makedirs(self.report_dir, exist_ok=True)
        self.styles = getSampleStyleSheet()
        # Add custom styles
        self.styles.add(ParagraphStyle(
            name='CustomHeading1',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        ))
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=12
        ))

    def _get_mood_data(self, days=30):
        """Get mood data for the last n days."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        entries = MoodEntry.query.filter(
            MoodEntry.user_id == self.user.id,
            MoodEntry.timestamp >= cutoff_date
        ).order_by(MoodEntry.timestamp).all()
        
        dates = [entry.timestamp for entry in entries]
        scores = [entry.mood_score for entry in entries]
        return dates, scores

    def _get_sentiment_data(self, days=30):
        """Get conversation sentiment data for the last n days."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        conversations = Conversation.query.filter(
            Conversation.user_id == self.user.id,
            Conversation.timestamp >= cutoff_date,
            Conversation.sentiment_score.isnot(None)
        ).order_by(Conversation.timestamp).all()
        
        return [conv.sentiment_score for conv in conversations]

    def _get_responses(self, days=30):
        """Get user responses for the last n days."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        responses = UserResponse.query.filter(
            UserResponse.user_id == self.user.id,
            UserResponse.timestamp >= cutoff_date
        ).order_by(UserResponse.timestamp.desc()).all()
        
        return responses

    def _generate_mood_plot(self):
        """Generate mood trend plot."""
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        mood_entries = MoodEntry.query.filter(
            MoodEntry.user_id == self.user.id,
            MoodEntry.timestamp >= thirty_days_ago
        ).order_by(MoodEntry.timestamp).all()
        
        if not mood_entries:
            return
        
        dates = [entry.timestamp.date() for entry in mood_entries]
        scores = [entry.mood_score for entry in mood_entries]
        
        plt.figure(figsize=(10, 6))
        plt.plot(dates, scores, marker='o')
        plt.title('Mood Trend (Last 30 Days)')
        plt.xlabel('Date')
        plt.ylabel('Mood Score')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        plt.savefig(os.path.join(self.report_dir, 'mood_plot.png'))
        plt.close()

    def _generate_survey_plots(self):
        """Generate plots for survey data analysis."""
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        surveys = Survey.query.filter(
            Survey.user_id == self.user.id,
            Survey.date >= thirty_days_ago
        ).order_by(Survey.date).all()
        
        if not surveys:
            return
            
        # Activity frequency plot
        activity_counts = Counter()
        for survey in surveys:
            activities = survey.get_activities()
            activity_counts.update(activities)
            
        activities = list(activity_counts.keys())
        counts = list(activity_counts.values())
        
        plt.figure(figsize=(10, 6))
        plt.bar(activities, counts)
        plt.title('Activity Frequency (Last 30 Days)')
        plt.xlabel('Activity')
        plt.ylabel('Count')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        plt.savefig(os.path.join(self.report_dir, 'activity_plot.png'))
        plt.close()
        
        # Social media time distribution
        social_media_counts = Counter(survey.social_media_time for survey in surveys)
        labels = [option['label'] for option in SOCIAL_MEDIA_OPTIONS]
        sizes = [social_media_counts[option['value']] for option in SOCIAL_MEDIA_OPTIONS]
        colors = [option['color'] for option in SOCIAL_MEDIA_OPTIONS]
        
        plt.figure(figsize=(8, 8))
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%')
        plt.title('Social Media Usage Distribution')
        plt.axis('equal')
        
        plt.savefig(os.path.join(self.report_dir, 'social_media_plot.png'))
        plt.close()

    def _generate_insights(self, avg_mood, activity_counts, social_media_counts):
        """Generate insights based on the data."""
        insights = []
        
        # Mood-based insights
        if avg_mood >= 7:
            insights.append("Your mood has been consistently positive")
        elif avg_mood <= 4:
            insights.append("Consider increasing activities that boost your mood")
        
        # Activity-based insights
        if 'exercise' in activity_counts and activity_counts['exercise'] >= 15:
            insights.append("You've maintained a good exercise routine")
        elif 'exercise' in activity_counts and activity_counts['exercise'] < 5:
            insights.append("Consider incorporating more physical activity")
            
        if 'meditation' in activity_counts and activity_counts['meditation'] >= 10:
            insights.append("Regular meditation practice is beneficial for mental health")
            
        # Social media insights
        high_usage = sum(social_media_counts[opt['value']] for opt in SOCIAL_MEDIA_OPTIONS 
                        if opt['value'] in ['>5h', '3-5h'])
        if high_usage > len(social_media_counts) / 2:
            insights.append("Consider reducing social media usage for better mental well-being")
            
        return '\n    '.join(f'\item {insight}' for insight in insights)

    def generate_report(self):
        """Generate a comprehensive PDF report."""
        # Create report filename
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f'report_{self.user.id}_{timestamp}.pdf'
        filepath = os.path.join(self.report_dir, filename)

        # Generate plots
        self._generate_mood_plot()
        self._generate_survey_plots()

        # Create the PDF document
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        # Build the document content
        story = self._build_report_content()

        # Generate the PDF
        doc.build(story)

        # Create report record
        report = Report(user_id=self.user.id, filename=filename)
        db.session.add(report)
        db.session.commit()

        # Clean up plot files
        self._cleanup_plots()

        return report

    def _build_report_content(self):
        """Build the content for the PDF report."""
        story = []
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)

        # Title
        title = Paragraph(f"Mental Health Report for {self.user.name}", self.styles['CustomHeading1'])
        story.append(title)
        story.append(Spacer(1, 12))

        # Date
        date = Paragraph(f"Generated on {datetime.utcnow().strftime('%B %d, %Y')}", self.styles['CustomBody'])
        story.append(date)
        story.append(Spacer(1, 24))

        # Get data for analysis
        mood_entries = MoodEntry.query.filter(
            MoodEntry.user_id == self.user.id,
            MoodEntry.timestamp >= thirty_days_ago
        ).all()

        conversations = Conversation.query.filter(
            Conversation.user_id == self.user.id,
            Conversation.timestamp >= thirty_days_ago
        ).all()

        surveys = Survey.query.filter(
            Survey.user_id == self.user.id,
            Survey.date >= thirty_days_ago
        ).all()

        # Mood Analysis Section
        story.append(Paragraph("Mood Analysis", self.styles['Heading2']))
        story.append(Spacer(1, 12))

        mood_scores = [entry.mood_score for entry in mood_entries]
        avg_mood = sum(mood_scores) / len(mood_scores) if mood_scores else 0

        sentiment_scores = [msg.sentiment_score for msg in conversations if msg.sentiment_score is not None]
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0

        mood_stats = [
            f"Average mood score: {avg_mood:.2f} / 10",
            f"Number of mood entries: {len(mood_entries)}",
            f"Average conversation sentiment: {avg_sentiment:.2f}"
        ]

        for stat in mood_stats:
            story.append(Paragraph(f"• {stat}", self.styles['CustomBody']))

        # Add mood plot
        if os.path.exists(os.path.join(self.report_dir, 'mood_plot.png')):
            story.append(Spacer(1, 12))
            story.append(Image(os.path.join(self.report_dir, 'mood_plot.png'), width=6*inch, height=4*inch))

        # Survey Analysis Section
        story.append(Paragraph("Daily Surveys Analysis", self.styles['Heading2']))
        story.append(Spacer(1, 12))

        # Activity analysis
        activity_counts = Counter()
        social_media_counts = Counter()
        custom_activities = []

        for survey in surveys:
            activities = survey.get_activities()
            activity_counts.update(activities)
            social_media_counts[survey.social_media_time] += 1
            custom_acts = survey.get_custom_activities()
            if custom_acts:
                custom_activities.extend(custom_acts)

        story.append(Paragraph(f"Total surveys completed: {len(surveys)}", self.styles['CustomBody']))
        story.append(Spacer(1, 12))

        # Most frequent activities
        story.append(Paragraph("Most Frequent Activities:", self.styles['CustomBody']))
        for act_id, count in activity_counts.most_common(5):
            activity = get_activity_by_id(act_id)
            if activity:
                story.append(Paragraph(f"• {activity['label']}: {count} times", self.styles['CustomBody']))

        # Add activity plot
        if os.path.exists(os.path.join(self.report_dir, 'activity_plot.png')):
            story.append(Spacer(1, 12))
            story.append(Image(os.path.join(self.report_dir, 'activity_plot.png'), width=6*inch, height=4*inch))

        # Social Media Usage
        story.append(Paragraph("Social Media Usage", self.styles['Heading2']))
        story.append(Spacer(1, 12))

        for option in SOCIAL_MEDIA_OPTIONS:
            if option['value'] in social_media_counts:
                count = social_media_counts[option['value']]
                percentage = (count / len(surveys)) * 100 if surveys else 0
                story.append(Paragraph(
                    f"• {option['label']}: {count} days ({percentage:.1f}%)",
                    self.styles['CustomBody']
                ))

        # Add social media plot
        if os.path.exists(os.path.join(self.report_dir, 'social_media_plot.png')):
            story.append(Spacer(1, 12))
            story.append(Image(os.path.join(self.report_dir, 'social_media_plot.png'), width=6*inch, height=4*inch))

        # Custom Activities
        if custom_activities:
            story.append(Paragraph("Custom Activities", self.styles['Heading2']))
            story.append(Spacer(1, 12))
            for activity in set(custom_activities):
                story.append(Paragraph(f"• {activity}", self.styles['CustomBody']))

        # Insights and Recommendations
        story.append(Paragraph("Insights and Recommendations", self.styles['Heading2']))
        story.append(Spacer(1, 12))

        insights = self._generate_insights(avg_mood, activity_counts, social_media_counts)
        for insight in insights.split('\item')[1:]:  # Skip empty first split
            story.append(Paragraph(f"• {insight.strip()}", self.styles['CustomBody']))

        return story

    def _cleanup_plots(self):
        """Clean up temporary plot files."""
        plot_files = ['mood_plot.png', 'activity_plot.png', 'social_media_plot.png']
        for plot_file in plot_files:
            try:
                os.remove(os.path.join(self.report_dir, plot_file))
            except OSError:
                pass 