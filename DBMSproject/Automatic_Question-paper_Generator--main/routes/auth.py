"""
Authentication Routes
---------------------
Handles faculty login, logout, and session management.
Provides login_required decorator for protected routes.
"""

from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from utils.db import execute_query

auth_bp = Blueprint('auth', __name__)


def login_required(f):
    """
    Decorator to protect routes that require authentication.
    Redirects to login page if faculty is not logged in.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'faculty_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Faculty login page and authentication handler."""

    # Redirect if already logged in
    if 'faculty_id' in session:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        # Validate input
        if not email or not password:
            flash('Please enter both email and password.', 'danger')
            return render_template('login.html')

        # Look up faculty by email
        faculty = execute_query(
            "SELECT * FROM Faculty WHERE email = %s",
            (email,),
            fetchone=True
        )

        if faculty and check_password_hash(faculty['password_hash'], password):
            # Successful login — store session data
            session['faculty_id'] = faculty['faculty_id']
            session['faculty_name'] = faculty['name']
            session['faculty_email'] = faculty['email']
            session['faculty_department'] = faculty['department']
            session.permanent = True

            flash(f'Welcome back, {faculty["name"]}!', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """Clear session and log out faculty."""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
