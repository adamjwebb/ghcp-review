"""
Security configuration for Flask application
"""

import os


class SecurityConfig:
    """Security configuration class"""
    
    # Flask secret key - should be set via environment variable
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    
    # Security headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'"
    }
    
    # Rate limiting
    RATELIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'true').lower() == 'true'
    RATELIMIT_DEFAULT = "60 per minute"
    RATELIMIT_STORAGE_URL = "memory://"
    
    # Database connection security
    DB_CONNECTION_TIMEOUT = 30
    DB_ENCRYPT = True
    DB_TRUST_SERVER_CERTIFICATE = False
    
    # Input validation
    MAX_USER_ID = 2147483647  # SQL Server INT max
    MIN_USER_ID = 1
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


class DevelopmentConfig(SecurityConfig):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(SecurityConfig):
    """Production configuration"""
    DEBUG = False
    TESTING = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
}
