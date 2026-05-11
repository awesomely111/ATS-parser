"""
Database Models for ATS
"""
from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    degree = db.Column(db.String(100))
    college = db.Column(db.String(200))
    graduation_year = db.Column(db.String(4))
    cgpa = db.Column(db.String(10))
    ms_office_skills = db.Column(db.String(50))
    inventory_experience = db.Column(db.Text)
    cover_letter = db.Column(db.Text)
    resume_path = db.Column(db.String(300))
    resume_text = db.Column(db.Text)

    # AI Scores
    tfidf_score = db.Column(db.Float, default=0)
    semantic_score = db.Column(db.Float, default=0)
    keyword_score = db.Column(db.Float, default=0)
    experience_score = db.Column(db.Float, default=0)
    education_score = db.Column(db.Float, default=0)
    overall_fit_score = db.Column(db.Float, default=0)
    matched_keywords = db.Column(db.Text)

    application_status = db.Column(db.String(50), default='applied')
    screening_status = db.Column(db.String(50), default='pending')
    screening_reason = db.Column(db.Text)

    interview_date = db.Column(db.DateTime)
    interview_time = db.Column(db.String(10))
    interview_feedback = db.Column(db.Text)

    submitted_on = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class EmailLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id'))
    recipient_email = db.Column(db.String(120))
    subject = db.Column(db.String(200))
    email_type = db.Column(db.String(50))
    status = db.Column(db.String(20), default='pending')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_query = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)
    response_type = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
