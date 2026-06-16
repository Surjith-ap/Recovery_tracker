"""
Reports route — upload, preview, manage medical reports
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory
from datetime import datetime
from models.db import db, Report
from models.schemas import REPORT_CATEGORIES, REPORT_CATEGORY_CONFIG
from werkzeug.utils import secure_filename
from config import Config
import os

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def get_file_size_str(size_bytes):
    """Convert bytes to human readable string"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


@reports_bp.route('/')
def index():
    """Display all reports with category filtering"""
    filter_category = request.args.get('category', 'all')

    query = Report.query

    if filter_category != 'all':
        query = query.filter_by(category=filter_category)

    reports = query.order_by(Report.report_date.desc()).all()

    # Count by category
    category_counts = {}
    for cat_key, cat_label in REPORT_CATEGORIES:
        category_counts[cat_key] = Report.query.filter_by(category=cat_key).count()

    return render_template('reports.html',
        reports=reports,
        categories=REPORT_CATEGORIES,
        category_config=REPORT_CATEGORY_CONFIG,
        category_counts=category_counts,
        current_filter=filter_category,
        get_file_size_str=get_file_size_str,
    )


@reports_bp.route('/upload', methods=['POST'])
def upload_report():
    """Upload a new medical report"""
    title = request.form.get('title')
    category = request.form.get('category')
    report_date = request.form.get('report_date')
    notes = request.form.get('notes')

    if not title or not category or not report_date:
        flash('Please fill in all required fields.', 'error')
        return redirect(url_for('reports.index'))

    if 'report_file' not in request.files:
        flash('No file selected.', 'error')
        return redirect(url_for('reports.index'))

    file = request.files['report_file']

    if file.filename == '':
        flash('No file selected.', 'error')
        return redirect(url_for('reports.index'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        ext = filename.rsplit('.', 1)[1].lower()
        safe_name = timestamp + filename
        
        # Upload using storage util
        from utils.storage import upload_file
        file_size = upload_file(file, safe_name)

        report = Report(
            title=title,
            category=category,
            report_date=datetime.strptime(report_date, '%Y-%m-%d').date(),
            file_path=safe_name,
            file_type=ext,
            file_size=file_size,
            notes=notes,
        )
        db.session.add(report)
        db.session.commit()
        flash('Report uploaded successfully!', 'success')
    else:
        flash('Invalid file type. Allowed: PDF, JPG, PNG, JPEG', 'error')

    return redirect(url_for('reports.index'))


@reports_bp.route('/download/<int:report_id>')
def download_report(report_id):
    """Download a report file"""
    report = Report.query.get_or_404(report_id)
    
    from utils.storage import get_file_url
    url = get_file_url(report.file_path)
    if url:
        return redirect(url)
        
    return send_from_directory(
        Config.UPLOAD_FOLDER,
        report.file_path,
        as_attachment=True,
        download_name=report.title + '.' + report.file_type
    )


@reports_bp.route('/view/<int:report_id>')
def view_report(report_id):
    """View/preview a report file inline"""
    report = Report.query.get_or_404(report_id)
    
    from utils.storage import get_file_url
    url = get_file_url(report.file_path)
    if url:
        return redirect(url)
        
    return send_from_directory(
        Config.UPLOAD_FOLDER,
        report.file_path,
    )


@reports_bp.route('/delete/<int:report_id>', methods=['POST'])
def delete_report(report_id):
    """Delete a report and its file"""
    report = Report.query.get_or_404(report_id)

    # Delete the physical file
    from utils.storage import delete_file
    delete_file(report.file_path)

    db.session.delete(report)
    db.session.commit()
    flash('Report deleted.', 'success')
    return redirect(url_for('reports.index'))
