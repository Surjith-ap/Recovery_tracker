"""
Timeline route — chronological treatment events
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from models.db import db, TimelineEvent
from models.schemas import ACTIVITY_TYPES, ACTIVITY_TYPE_CONFIG
from werkzeug.utils import secure_filename
from config import Config
import os

timeline_bp = Blueprint('timeline', __name__, url_prefix='/timeline')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


@timeline_bp.route('/')
def index():
    """Display all timeline events"""
    filter_type = request.args.get('type', 'all')

    query = TimelineEvent.query

    if filter_type != 'all':
        query = query.filter_by(activity_type=filter_type)

    events = query.order_by(TimelineEvent.event_date.desc()).all()

    return render_template('timeline.html',
        events=events,
        activity_types=ACTIVITY_TYPES,
        activity_config=ACTIVITY_TYPE_CONFIG,
        current_filter=filter_type,
    )


@timeline_bp.route('/add', methods=['POST'])
def add_event():
    """Add a new timeline event"""
    event_date = request.form.get('event_date')
    activity_type = request.form.get('activity_type')
    title = request.form.get('title')
    description = request.form.get('description')

    if not event_date or not activity_type or not title:
        flash('Please fill in all required fields.', 'error')
        return redirect(url_for('timeline.index'))

    attachment_path = None
    if 'attachment' in request.files:
        file = request.files['attachment']
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            filename = timestamp + filename
            file.save(os.path.join(Config.UPLOAD_FOLDER, filename))
            attachment_path = filename

    event = TimelineEvent(
        event_date=datetime.strptime(event_date, '%Y-%m-%d').date(),
        activity_type=activity_type,
        title=title,
        description=description,
        attachment_path=attachment_path,
    )
    db.session.add(event)
    db.session.commit()
    flash('Timeline event added successfully!', 'success')
    return redirect(url_for('timeline.index'))


@timeline_bp.route('/delete/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    """Delete a timeline event"""
    event = TimelineEvent.query.get_or_404(event_id)

    # Delete attachment file if exists
    if event.attachment_path:
        filepath = os.path.join(Config.UPLOAD_FOLDER, event.attachment_path)
        if os.path.exists(filepath):
            os.remove(filepath)

    db.session.delete(event)
    db.session.commit()
    flash('Timeline event deleted.', 'success')
    return redirect(url_for('timeline.index'))


@timeline_bp.route('/edit/<int:event_id>', methods=['POST'])
def edit_event(event_id):
    """Edit a timeline event"""
    event = TimelineEvent.query.get_or_404(event_id)

    event.event_date = datetime.strptime(request.form.get('event_date'), '%Y-%m-%d').date()
    event.activity_type = request.form.get('activity_type')
    event.title = request.form.get('title')
    event.description = request.form.get('description')

    if 'attachment' in request.files:
        file = request.files['attachment']
        if file and file.filename and allowed_file(file.filename):
            # Remove old attachment
            if event.attachment_path:
                old_path = os.path.join(Config.UPLOAD_FOLDER, event.attachment_path)
                if os.path.exists(old_path):
                    os.remove(old_path)
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            filename = timestamp + filename
            file.save(os.path.join(Config.UPLOAD_FOLDER, filename))
            event.attachment_path = filename

    db.session.commit()
    flash('Timeline event updated.', 'success')
    return redirect(url_for('timeline.index'))
