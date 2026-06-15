"""
Medications route — medication tracking
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from models.db import db, Medication
from models.schemas import MEDICATION_STATUS

medications_bp = Blueprint('medications', __name__, url_prefix='/medications')


@medications_bp.route('/')
def index():
    filter_status = request.args.get('status', 'all')
    query = Medication.query
    if filter_status != 'all':
        query = query.filter_by(status=filter_status)
    medications = query.order_by(Medication.start_date.desc()).all()
    active_count = Medication.query.filter_by(status='active').count()
    completed_count = Medication.query.filter_by(status='completed').count()
    discontinued_count = Medication.query.filter_by(status='discontinued').count()
    return render_template('medications.html',
        medications=medications, statuses=MEDICATION_STATUS,
        current_filter=filter_status, active_count=active_count,
        completed_count=completed_count, discontinued_count=discontinued_count)


@medications_bp.route('/add', methods=['POST'])
def add_medication():
    medicine_name = request.form.get('medicine_name')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    dosage = request.form.get('dosage')
    frequency = request.form.get('frequency')
    instructions = request.form.get('instructions')
    status = request.form.get('status', 'active')
    prescribed_by = request.form.get('prescribed_by')
    if not medicine_name or not start_date or not dosage or not frequency:
        flash('Please fill in all required fields.', 'error')
        return redirect(url_for('medications.index'))
    medication = Medication(
        medicine_name=medicine_name,
        start_date=datetime.strptime(start_date, '%Y-%m-%d').date(),
        end_date=datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None,
        dosage=dosage, frequency=frequency, instructions=instructions,
        status=status, prescribed_by=prescribed_by)
    db.session.add(medication)
    db.session.commit()
    flash('Medication added successfully!', 'success')
    return redirect(url_for('medications.index'))


@medications_bp.route('/delete/<int:med_id>', methods=['POST'])
def delete_medication(med_id):
    medication = Medication.query.get_or_404(med_id)
    db.session.delete(medication)
    db.session.commit()
    flash('Medication deleted.', 'success')
    return redirect(url_for('medications.index'))


@medications_bp.route('/edit/<int:med_id>', methods=['POST'])
def edit_medication(med_id):
    medication = Medication.query.get_or_404(med_id)
    medication.medicine_name = request.form.get('medicine_name')
    medication.start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
    end_date = request.form.get('end_date')
    medication.end_date = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
    medication.dosage = request.form.get('dosage')
    medication.frequency = request.form.get('frequency')
    medication.instructions = request.form.get('instructions')
    medication.status = request.form.get('status', medication.status)
    medication.prescribed_by = request.form.get('prescribed_by')
    db.session.commit()
    flash('Medication updated.', 'success')
    return redirect(url_for('medications.index'))


@medications_bp.route('/update-status/<int:med_id>', methods=['POST'])
def update_status(med_id):
    medication = Medication.query.get_or_404(med_id)
    new_status = request.form.get('status')
    if new_status in ['active', 'completed', 'discontinued']:
        medication.status = new_status
        db.session.commit()
        flash(f'Status updated to {new_status}.', 'success')
    return redirect(url_for('medications.index'))
