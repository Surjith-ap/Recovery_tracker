"""
Journal route — daily recovery journal
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime, date
from models.db import db, JournalEntry

journal_bp = Blueprint('journal', __name__, url_prefix='/journal')


@journal_bp.route('/')
def index():
    entries = JournalEntry.query.order_by(JournalEntry.entry_date.desc()).all()
    today_entry = JournalEntry.query.filter_by(entry_date=date.today()).first()
    return render_template('journal.html', entries=entries, today_entry=today_entry)


@journal_bp.route('/add', methods=['POST'])
def add_entry():
    entry_date = request.form.get('entry_date')
    symptoms = request.form.get('symptoms')
    energy_level = request.form.get('energy_level')
    appetite = request.form.get('appetite')
    sleep_quality = request.form.get('sleep_quality')
    mood = request.form.get('mood')
    observations = request.form.get('observations')
    recovery_notes = request.form.get('recovery_notes')

    if not entry_date:
        flash('Date is required.', 'error')
        return redirect(url_for('journal.index'))

    parsed_date = datetime.strptime(entry_date, '%Y-%m-%d').date()
    existing = JournalEntry.query.filter_by(entry_date=parsed_date).first()
    if existing:
        existing.symptoms = symptoms
        existing.energy_level = int(energy_level) if energy_level else None
        existing.appetite = int(appetite) if appetite else None
        existing.sleep_quality = int(sleep_quality) if sleep_quality else None
        existing.mood = int(mood) if mood else None
        existing.observations = observations
        existing.recovery_notes = recovery_notes
        db.session.commit()
        flash('Journal entry updated!', 'success')
    else:
        entry = JournalEntry(
            entry_date=parsed_date, symptoms=symptoms,
            energy_level=int(energy_level) if energy_level else None,
            appetite=int(appetite) if appetite else None,
            sleep_quality=int(sleep_quality) if sleep_quality else None,
            mood=int(mood) if mood else None,
            observations=observations, recovery_notes=recovery_notes)
        db.session.add(entry)
        db.session.commit()
        flash('Journal entry added!', 'success')
    return redirect(url_for('journal.index'))


@journal_bp.route('/delete/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    entry = JournalEntry.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    flash('Journal entry deleted.', 'success')
    return redirect(url_for('journal.index'))
