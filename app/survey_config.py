"""Configuration module for survey options and settings."""

# Activity options for daily surveys
ACTIVITY_OPTIONS = [
    {
        'id': 'work',
        'label': 'Work/Study',
        'icon': 'fa-briefcase',
        'category': 'productivity'
    },
    {
        'id': 'exercise',
        'label': 'Exercise',
        'icon': 'fa-dumbbell',
        'category': 'health'
    },
    {
        'id': 'meditation',
        'label': 'Meditation/Relaxation',
        'icon': 'fa-peace',
        'category': 'wellness'
    },
    {
        'id': 'socializing',
        'label': 'Socializing',
        'icon': 'fa-users',
        'category': 'social'
    },
    {
        'id': 'hobbies',
        'label': 'Hobbies',
        'icon': 'fa-palette',
        'category': 'leisure'
    },
    {
        'id': 'learning',
        'label': 'Learning/Reading',
        'icon': 'fa-book',
        'category': 'education'
    },
    {
        'id': 'outdoors',
        'label': 'Outdoor Activities',
        'icon': 'fa-tree',
        'category': 'health'
    },
    {
        'id': 'creative',
        'label': 'Creative Work',
        'icon': 'fa-pencil-alt',
        'category': 'leisure'
    }
]

# Social media time options
SOCIAL_MEDIA_OPTIONS = [
    {
        'id': 'lt1',
        'label': 'Less than 1 hour',
        'value': '<1h',
        'color': 'green'
    },
    {
        'id': '1to3',
        'label': '1-3 hours',
        'value': '1-3h',
        'color': 'yellow'
    },
    {
        'id': '3to5',
        'label': '3-5 hours',
        'value': '3-5h',
        'color': 'orange'
    },
    {
        'id': 'gt5',
        'label': 'More than 5 hours',
        'value': '>5h',
        'color': 'red'
    }
]

# Activity categories for grouping and analysis
ACTIVITY_CATEGORIES = {
    'productivity': 'Work and Study',
    'health': 'Physical Health',
    'wellness': 'Mental Wellness',
    'social': 'Social Activities',
    'leisure': 'Leisure Time',
    'education': 'Learning'
}

# Survey settings
SURVEY_SETTINGS = {
    'max_custom_activities': 3,  # Maximum number of custom activities per survey
    'custom_activity_max_length': 50,  # Maximum length of custom activity text
    'allow_multiple_daily': False,  # Whether to allow multiple surveys per day
    'reminder_hour': 20,  # Hour of day (24h format) to send reminders
    'analysis_window_days': 30  # Number of days to analyze for reports
}

def get_activity_by_id(activity_id):
    """Get activity details by ID."""
    return next((a for a in ACTIVITY_OPTIONS if a['id'] == activity_id), None)

def get_social_media_option(value):
    """Get social media option details by value."""
    return next((s for s in SOCIAL_MEDIA_OPTIONS if s['value'] == value), None)

def validate_activities(activities):
    """Validate selected activities against predefined options."""
    valid_ids = {a['id'] for a in ACTIVITY_OPTIONS}
    return all(activity in valid_ids for activity in activities)

def validate_social_media_time(time_value):
    """Validate social media time against predefined options."""
    valid_values = {s['value'] for s in SOCIAL_MEDIA_OPTIONS}
    return time_value in valid_values 