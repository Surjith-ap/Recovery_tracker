"""
Dashboard route — main summary page
"""
from flask import Blueprint, render_template
from datetime import date, datetime
from models.db import db, TimelineEvent, LabResult, Report, Medication, JournalEntry
from config import Config

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def index():
    """Main dashboard view with summary cards and charts"""
    today = date.today()
    diagnosis_date = datetime.strptime(Config.DIAGNOSIS_DATE, '%Y-%m-%d').date()
    days_since_diagnosis = (today - diagnosis_date).days

    # Summary counts
    total_consultations = TimelineEvent.query.filter(
        TimelineEvent.activity_type.in_(['consultation', 'ayurveda_visit', 'hospital_visit'])
    ).count()
    total_tests = LabResult.query.count()
    active_medications = Medication.query.filter_by(status='active').count()
    total_reports = Report.query.count()
    total_milestones = TimelineEvent.query.filter_by(activity_type='recovery_milestone').count()

    # Latest bilirubin reading
    latest_bilirubin = LabResult.query.filter(
        LabResult.test_name.like('%Bilirubin%')
    ).order_by(LabResult.test_date.desc()).first()

    # Latest test date
    latest_test = LabResult.query.order_by(LabResult.test_date.desc()).first()

    # Upcoming / latest consultation
    latest_consultation = TimelineEvent.query.filter(
        TimelineEvent.activity_type.in_(['consultation', 'ayurveda_visit'])
    ).order_by(TimelineEvent.event_date.desc()).first()

    # Recent timeline events (last 5)
    recent_events = TimelineEvent.query.order_by(
        TimelineEvent.event_date.desc()
    ).limit(5).all()

    # Recent journal entries (last 3)
    recent_journals = JournalEntry.query.order_by(
        JournalEntry.entry_date.desc()
    ).limit(3).all()

    # Bilirubin trend data for chart
    bilirubin_data = LabResult.query.filter(
        LabResult.test_name.like('%Total Bilirubin%')
    ).order_by(LabResult.test_date.asc()).all()

    bilirubin_dates = [r.test_date.strftime('%b %d') for r in bilirubin_data]
    bilirubin_values = [float(r.result_value) if r.result_value else 0 for r in bilirubin_data]

    # LFT trend data (SGPT/SGOT)
    sgpt_data = LabResult.query.filter(
        LabResult.test_name.like('%SGPT%')
    ).order_by(LabResult.test_date.asc()).all()

    sgot_data = LabResult.query.filter(
        LabResult.test_name.like('%SGOT%')
    ).order_by(LabResult.test_date.asc()).all()

    # Active medications list
    active_meds = Medication.query.filter_by(status='active').order_by(
        Medication.start_date.desc()
    ).limit(5).all()

    return render_template('dashboard.html',
        days_since_diagnosis=days_since_diagnosis,
        diagnosis_date=diagnosis_date,
        total_consultations=total_consultations,
        total_tests=total_tests,
        active_medications=active_medications,
        total_reports=total_reports,
        total_milestones=total_milestones,
        latest_bilirubin=latest_bilirubin,
        latest_test=latest_test,
        latest_consultation=latest_consultation,
        recent_events=recent_events,
        recent_journals=recent_journals,
        bilirubin_dates=bilirubin_dates,
        bilirubin_values=bilirubin_values,
        sgpt_data=sgpt_data,
        sgot_data=sgot_data,
        active_meds=active_meds,
    )
