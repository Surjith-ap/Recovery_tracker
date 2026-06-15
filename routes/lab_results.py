"""
Lab Results route — medical test tracking
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from models.db import db, LabResult
from models.schemas import LAB_TEST_NAMES, LAB_RESULT_STATUS

lab_results_bp = Blueprint('lab_results', __name__, url_prefix='/lab-results')


@lab_results_bp.route('/')
def index():
    """Display all lab results with filtering"""
    filter_test = request.args.get('test', 'all')

    query = LabResult.query

    if filter_test != 'all':
        query = query.filter_by(test_name=filter_test)

    results = query.order_by(LabResult.test_date.desc()).all()

    # Get unique test names from DB for filter dropdown
    test_names_in_db = db.session.query(LabResult.test_name).distinct().all()
    test_names_in_db = [t[0] for t in test_names_in_db]

    return render_template('lab_results.html',
        results=results,
        test_names=LAB_TEST_NAMES,
        test_names_in_db=test_names_in_db,
        result_statuses=LAB_RESULT_STATUS,
        current_filter=filter_test,
    )


@lab_results_bp.route('/add', methods=['POST'])
def add_result():
    """Add a new lab result"""
    test_name = request.form.get('test_name')
    if test_name == 'Other':
        test_name = request.form.get('custom_test_name', 'Other')
    test_date = request.form.get('test_date')
    result_value = request.form.get('result_value')
    result_unit = request.form.get('result_unit')
    normal_range = request.form.get('normal_range')
    status = request.form.get('status')
    doctor_notes = request.form.get('doctor_notes')
    followup_recommendations = request.form.get('followup_recommendations')

    if not test_name or not test_date:
        flash('Test name and date are required.', 'error')
        return redirect(url_for('lab_results.index'))

    result = LabResult(
        test_name=test_name,
        test_date=datetime.strptime(test_date, '%Y-%m-%d').date(),
        result_value=result_value,
        result_unit=result_unit,
        normal_range=normal_range,
        status=status,
        doctor_notes=doctor_notes,
        followup_recommendations=followup_recommendations,
    )
    db.session.add(result)
    db.session.commit()
    flash('Lab result added successfully!', 'success')
    return redirect(url_for('lab_results.index'))


@lab_results_bp.route('/delete/<int:result_id>', methods=['POST'])
def delete_result(result_id):
    """Delete a lab result"""
    result = LabResult.query.get_or_404(result_id)
    db.session.delete(result)
    db.session.commit()
    flash('Lab result deleted.', 'success')
    return redirect(url_for('lab_results.index'))


@lab_results_bp.route('/edit/<int:result_id>', methods=['POST'])
def edit_result(result_id):
    """Edit a lab result"""
    result = LabResult.query.get_or_404(result_id)

    test_name = request.form.get('test_name')
    if test_name == 'Other':
        test_name = request.form.get('custom_test_name', result.test_name)

    result.test_name = test_name
    result.test_date = datetime.strptime(request.form.get('test_date'), '%Y-%m-%d').date()
    result.result_value = request.form.get('result_value')
    result.result_unit = request.form.get('result_unit')
    result.normal_range = request.form.get('normal_range')
    result.status = request.form.get('status')
    result.doctor_notes = request.form.get('doctor_notes')
    result.followup_recommendations = request.form.get('followup_recommendations')

    db.session.commit()
    flash('Lab result updated.', 'success')
    return redirect(url_for('lab_results.index'))


@lab_results_bp.route('/api/chart-data')
def chart_data():
    """API endpoint for chart data"""
    test_name = request.args.get('test', 'Total Bilirubin')

    results = LabResult.query.filter(
        LabResult.test_name.like(f'%{test_name}%')
    ).order_by(LabResult.test_date.asc()).all()

    data = {
        'labels': [r.test_date.strftime('%b %d, %Y') for r in results],
        'values': [float(r.result_value) if r.result_value else 0 for r in results],
        'test_name': test_name,
    }
    return jsonify(data)
