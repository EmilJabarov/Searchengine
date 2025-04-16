from app.models import User, UserSettings
from app import db
from datetime import datetime

class UserService:
    @staticmethod
    def create_user(username, password):
        try:
            user = User(username=username, password=password)
            settings = UserSettings(user=user)
            db.session.add(user)
            db.session.add(settings)
            db.session.commit()
            return user
        except Exception as e:
            print(f"Error creating user: {e}")
            db.session.rollback()
            return None

    @staticmethod
    def update_last_login(user):
        try:
            user.last_login = datetime.utcnow()
            db.session.commit()
        except Exception as e:
            print(f"Error updating last login: {e}")
            db.session.rollback()

    @staticmethod
    def update_preferences(user, preferences):
        try:
            user.preferences = preferences
            db.session.commit()
            return True
        except Exception as e:
            print(f"Error updating preferences: {e}")
            db.session.rollback()
            return False

    @staticmethod
    def update_settings(user, settings_data):
        try:
            if not user.settings:
                user.settings = UserSettings(user=user)
            
            for key, value in settings_data.items():
                if hasattr(user.settings, key):
                    setattr(user.settings, key, value)
            
            db.session.commit()
            return True
        except Exception as e:
            print(f"Error updating settings: {e}")
            db.session.rollback()
            return False