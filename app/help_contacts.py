"""Module containing help contact information."""

HELP_CONTACTS = [
    {
        'name': 'Crisis Helpline',
        'contact': '116 123',
        'description': 'Free, 24/7 crisis support line for emotional support.',
        'category': 'emergency',
        'hours': '24/7'
    },
    {
        'name': 'Psychologist Directory',
        'contact': 'www.psycholog.pl',
        'description': 'Find licensed psychologists and therapists in your area.',
        'category': 'directory',
        'hours': 'Online directory available 24/7'
    },
    {
        'name': 'Mental Health Center',
        'contact': '+48 22 123 4567',
        'description': 'Professional mental health services and consultations.',
        'category': 'professional',
        'hours': 'Mon-Fri: 8:00-20:00'
    },
    {
        'name': 'Youth Support Line',
        'contact': '116 111',
        'description': 'Dedicated helpline for children and teenagers.',
        'category': 'youth',
        'hours': 'Daily: 12:00-22:00'
    },
    {
        'name': 'Online Therapy Platform',
        'contact': 'www.terapiaonline.pl',
        'description': 'Connect with licensed therapists online.',
        'category': 'online',
        'hours': '24/7 platform access'
    },
    {
        'name': 'Emergency Services',
        'contact': '112',
        'description': 'For immediate emergency assistance.',
        'category': 'emergency',
        'hours': '24/7'
    }
]

def get_contacts_by_category(category=None):
    """Get contacts filtered by category."""
    if category:
        return [contact for contact in HELP_CONTACTS if contact['category'] == category]
    return HELP_CONTACTS

def get_emergency_contacts():
    """Get emergency contacts only."""
    return get_contacts_by_category('emergency') 