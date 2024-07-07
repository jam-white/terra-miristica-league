from functools import wraps

from flask import abort
from flask_login import current_user


def admin_required(func):
    @wraps(func)
    def wrapper_function(*args, **kwargs):
        if current_user.is_authenticated and current_user.id == 1:
            return func(*args, **kwargs)
        else:
            return abort(403)
    return wrapper_function
