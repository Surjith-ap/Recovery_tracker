"""
Auth route — login and logout for the single-user app.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from models.user import User
import os

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        expected_username = os.environ.get('ADMIN_USERNAME', 'admin')
        password_hash = os.environ.get('ADMIN_PASSWORD_HASH', '')

        if username == expected_username and check_password_hash(password_hash, password):
            user = User()
            login_user(user, remember=True)
            # Redirect to the page the user originally tried to visit
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))

        flash('Invalid username or password.', 'error')

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))
