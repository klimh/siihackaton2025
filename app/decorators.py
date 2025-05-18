from functools import wraps
from flask import abort
from flask_login import current_user

def admin_required(f):
    """
    Decorator to restrict routes to admin users only.
    Returns 403 (Forbidden) if the current user is not an admin.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function 