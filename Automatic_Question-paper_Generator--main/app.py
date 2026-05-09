"""
SmartQGen – Intelligent Internal Assessment Question Paper Generator
=====================================================================
Main Flask application entry point.
Registers all blueprints and configures the application.
"""

import os
import sys
from flask import Flask, redirect, url_for, render_template
from werkzeug.security import generate_password_hash
from config import Config


def create_app():
    """Application factory — creates and configures the Flask app."""

    app = Flask(__name__)
    app.config.from_object(Config)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.questions import questions_bp
    from routes.papers import papers_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(questions_bp)
    app.register_blueprint(papers_bp)

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template('base.html', error_code=404,
                               error_message='Page not found'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('base.html', error_code=500,
                               error_message='Internal server error'), 500

    return app


def seed_faculty_passwords():
    """
    Update seed data faculty passwords with proper hashes.
    Run this once after loading seed_data.sql.
    """
    from utils.db import execute_query

    password_hash = generate_password_hash('password123')

    # Update both seeded faculty members
    execute_query(
        "UPDATE Faculty SET password_hash = %s WHERE email = %s",
        (password_hash, 'anil.kumar@university.edu'),
        commit=True
    )
    execute_query(
        "UPDATE Faculty SET password_hash = %s WHERE email = %s",
        (password_hash, 'meera.sharma@university.edu'),
        commit=True
    )
    print("Faculty passwords updated successfully!")
    print("Login credentials:")
    print("  Email: anil.kumar@university.edu")
    print("  Password: password123")
    print("  ---")
    print("  Email: meera.sharma@university.edu")
    print("  Password: password123")


# Entry point
if __name__ == '__main__':
    app = create_app()

    # Check for --seed-passwords flag
    if '--seed-passwords' in sys.argv:
        with app.app_context():
            seed_faculty_passwords()
    else:
        # Create generated_papers directory
        os.makedirs('generated_papers', exist_ok=True)
        app.run(debug=True, host='0.0.0.0', port=5000)
