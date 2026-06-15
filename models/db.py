"""
Database models for Jaundice Recovery Tracker
Uses SQLite via Flask-SQLAlchemy
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

db = SQLAlchemy()


class TimelineEvent(db.Model):
    """Timeline events tracking all treatment activities"""
    __tablename__ = 'timeline_events'

    id = db.Column(db.Integer, primary_key=True)
    event_date = db.Column(db.Date, nullable=False, default=date.today)
    activity_type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    attachment_path = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Activity types: diagnosis, hospital_visit, lab_test, consultation,
    # ayurveda_visit, medication_purchase, recovery_milestone

    def to_dict(self):
        return {
            'id': self.id,
            'event_date': self.event_date.isoformat(),
            'activity_type': self.activity_type,
            'title': self.title,
            'description': self.description,
            'attachment_path': self.attachment_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class LabResult(db.Model):
    """Medical test results tracking"""
    __tablename__ = 'lab_results'

    id = db.Column(db.Integer, primary_key=True)
    test_name = db.Column(db.String(100), nullable=False)
    test_date = db.Column(db.Date, nullable=False, default=date.today)
    result_value = db.Column(db.String(50), nullable=True)
    result_unit = db.Column(db.String(30), nullable=True)
    normal_range = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(20), nullable=True)  # normal, high, low, critical
    doctor_notes = db.Column(db.Text, nullable=True)
    followup_recommendations = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'test_name': self.test_name,
            'test_date': self.test_date.isoformat(),
            'result_value': self.result_value,
            'result_unit': self.result_unit,
            'normal_range': self.normal_range,
            'status': self.status,
            'doctor_notes': self.doctor_notes,
            'followup_recommendations': self.followup_recommendations,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Report(db.Model):
    """Uploaded medical reports"""
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    report_date = db.Column(db.Date, nullable=False, default=date.today)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)
    file_size = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Categories: laboratory_report, prescription, consultation_notes, ayurveda_records

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'report_date': self.report_date.isoformat(),
            'file_path': self.file_path,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Medication(db.Model):
    """Medication tracking"""
    __tablename__ = 'medications'

    id = db.Column(db.Integer, primary_key=True)
    medicine_name = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.Date, nullable=False, default=date.today)
    end_date = db.Column(db.Date, nullable=True)
    dosage = db.Column(db.String(100), nullable=False)
    frequency = db.Column(db.String(100), nullable=False)
    instructions = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='active')
    prescribed_by = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Status: active, completed, discontinued

    def to_dict(self):
        return {
            'id': self.id,
            'medicine_name': self.medicine_name,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'dosage': self.dosage,
            'frequency': self.frequency,
            'instructions': self.instructions,
            'status': self.status,
            'prescribed_by': self.prescribed_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class JournalEntry(db.Model):
    """Daily recovery journal entries"""
    __tablename__ = 'journal_entries'

    id = db.Column(db.Integer, primary_key=True)
    entry_date = db.Column(db.Date, nullable=False, default=date.today, unique=True)
    symptoms = db.Column(db.Text, nullable=True)
    energy_level = db.Column(db.Integer, nullable=True)  # 1-10
    appetite = db.Column(db.Integer, nullable=True)  # 1-10
    sleep_quality = db.Column(db.Integer, nullable=True)  # 1-10
    mood = db.Column(db.Integer, nullable=True)  # 1-10
    observations = db.Column(db.Text, nullable=True)
    recovery_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'entry_date': self.entry_date.isoformat(),
            'symptoms': self.symptoms,
            'energy_level': self.energy_level,
            'appetite': self.appetite,
            'sleep_quality': self.sleep_quality,
            'mood': self.mood,
            'observations': self.observations,
            'recovery_notes': self.recovery_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


def init_db(app):
    """Initialize database and create all tables"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
