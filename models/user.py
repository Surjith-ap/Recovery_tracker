"""
User model for Flask-Login.
Single-user app — credentials come from environment variables.
No database table needed; the user object is a lightweight in-memory class.
"""
from flask_login import UserMixin


class User(UserMixin):
    """Represents the single authenticated user."""
    # Fixed ID since there is only ever one user
    id = '1'

    def get_id(self):
        return self.id

    @staticmethod
    def get(user_id):
        """Return the User instance if the ID matches, else None."""
        if user_id == '1':
            return User()
        return None
