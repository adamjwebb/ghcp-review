"""
Secure Python Flask API for Azure SQL Database

This application demonstrates security best practices including:
- Environment-based configuration (no hardcoded credentials)
- Parameterized queries to prevent SQL injection
- Input validation and sanitization
- Rate limiting
- Security headers
- Proper error handling
- Logging
"""

import os
import re
import logging
from typing import Optional, Tuple
from flask import Flask, request, jsonify, Response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import pyodbc
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', os.urandom(24))

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["60 per minute"] if os.getenv('RATE_LIMIT_ENABLED', 'true').lower() == 'true' else [],
    storage_uri="memory://"
)


class DatabaseConnection:
    """Secure database connection handler"""
    
    def __init__(self):
        self.server = os.getenv('DB_SERVER')
        self.database = os.getenv('DB_DATABASE')
        self.username = os.getenv('DB_USERNAME')
        self.password = os.getenv('DB_PASSWORD')
        self.driver = os.getenv('DB_DRIVER', '{ODBC Driver 18 for SQL Server}')
        
        # Validate required environment variables
        if not all([self.server, self.database, self.username, self.password]):
            raise ValueError("Database configuration incomplete. Check environment variables.")
    
    def get_connection_string(self) -> str:
        """Build secure connection string"""
        return (
            f'DRIVER={self.driver};'
            f'SERVER={self.server};'
            f'DATABASE={self.database};'
            f'UID={self.username};'
            f'PWD={self.password};'
            f'Encrypt=yes;'
            f'TrustServerCertificate=no;'
            f'Connection Timeout=30;'
        )
    
    def get_connection(self):
        """Get database connection with proper error handling"""
        try:
            conn = pyodbc.connect(self.get_connection_string())
            return conn
        except pyodbc.Error as e:
            logger.error(f"Database connection error: {str(e)}")
            raise


def validate_user_id(user_id: str) -> Tuple[bool, Optional[int], Optional[str]]:
    """
    Validate and sanitize user ID input
    
    Args:
        user_id: User ID from request parameter
        
    Returns:
        Tuple of (is_valid, sanitized_id, error_message)
    """
    if not user_id:
        return False, None, "User ID is required"
    
    # Check if it's a valid integer
    if not re.match(r'^\d+$', user_id):
        return False, None, "User ID must be a positive integer"
    
    try:
        id_int = int(user_id)
        if id_int <= 0:
            return False, None, "User ID must be greater than 0"
        if id_int > 2147483647:  # SQL Server INT max value
            return False, None, "User ID is too large"
        return True, id_int, None
    except (ValueError, OverflowError):
        return False, None, "Invalid user ID format"


@app.after_request
def add_security_headers(response: Response) -> Response:
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "user-api"}), 200


@app.route('/user', methods=['GET'])
@limiter.limit("30 per minute")
def get_user():
    """
    Get user by ID with security best practices
    
    Query Parameters:
        id: User ID (integer)
        
    Returns:
        JSON response with user data or error message
    """
    try:
        # Get and validate user ID
        user_id = request.args.get('id', '')
        is_valid, sanitized_id, error_msg = validate_user_id(user_id)
        
        if not is_valid:
            logger.warning(f"Invalid user ID attempt: {user_id}")
            return jsonify({"error": error_msg}), 400
        
        # Connect to database
        db = DatabaseConnection()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Use parameterized query to prevent SQL injection
        query = "SELECT id, username, email FROM users WHERE id = ?"
        cursor.execute(query, (sanitized_id,))
        
        row = cursor.fetchone()
        
        if row:
            user_data = {
                "id": row.id,
                "username": row.username,
                "email": row.email
            }
            logger.info(f"Successfully retrieved user {sanitized_id}")
            return jsonify(user_data), 200
        else:
            logger.info(f"User {sanitized_id} not found")
            return jsonify({"error": "User not found"}), 404
            
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        return jsonify({"error": "Service configuration error"}), 500
        
    except pyodbc.Error as e:
        logger.error(f"Database error: {str(e)}")
        return jsonify({"error": "Database error"}), 500
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
        
    finally:
        # Ensure connection is closed
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit exceeded"""
    logger.warning(f"Rate limit exceeded from {get_remote_address()}")
    return jsonify({"error": "Rate limit exceeded. Please try again later."}), 429


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(e)}")
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    # Verify environment configuration on startup
    try:
        db = DatabaseConnection()
        logger.info("Database configuration validated successfully")
    except ValueError as e:
        logger.error(f"Startup failed: {str(e)}")
        exit(1)
    
    # Run in production mode by default
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    
    if debug_mode:
        logger.warning("Running in DEBUG mode - not suitable for production!")
    
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=debug_mode
    )
