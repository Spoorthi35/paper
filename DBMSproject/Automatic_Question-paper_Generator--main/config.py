"""
SmartQGen Configuration
-----------------------
Database and application configuration settings.
Update MySQL credentials as needed.
"""

import os

class Config:
    """Base configuration class."""

    # Flask secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY', 'smartqgen-secret-key-change-in-production')

    # MySQL Database Configuration
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'smartqgen')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))

    # Session configuration
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour in seconds

    # Application settings
    DUPLICATE_CHECK_YEARS = 2  # Years to check for duplicate questions
    MAX_GENERATION_ATTEMPTS = 100  # Max attempts for paper generation algorithm
