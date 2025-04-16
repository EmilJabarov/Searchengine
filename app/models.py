from datetime import datetime
from flask_login import UserMixin
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    preferences = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    searches = db.relationship('Search', backref='user', lazy=True)
    settings = db.relationship('UserSettings', backref='user', uselist=False)

class Search(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_query = db.Column(db.String(200), nullable=False)
    modified_query = db.Column(db.String(200), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    results_count = db.Column(db.Integer)
    clicked_results = db.relationship('ClickedResult', backref='search', lazy=True)

class ClickedResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    search_id = db.Column(db.Integer, db.ForeignKey('search.id'), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class UserSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    theme = db.Column(db.String(20), default='dark')
    results_per_page = db.Column(db.Integer, default=10)
    auto_save_history = db.Column(db.Boolean, default=True)