from flask import Flask, request, jsonify
import pyodbc
import os
import logging
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configure logging for security events
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use environment variables for database credentials
server = os.getenv('DB_SERVER', 'your-azure-sql-server.database.windows.net')
database = os.getenv('DB_DATABASE', 'your-database')
username = os.getenv('DB_USERNAME', 'your-username')
password = os.getenv('DB_PASSWORD', 'your-password')
driver = os.getenv('DB_DRIVER', '{ODBC Driver 17 for SQL Server}')

def get_db_connection():
    try:
        conn = pyodbc.connect(
            f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}',
            timeout=30
        )
        return conn
    except pyodbc.Error as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise

def validate_user_id(user_id):
    """Validate user ID to prevent injection attacks"""
    if not user_id:
        return False
    # Only allow numeric values for user ID
    if not re.match(r'^\d+$', str(user_id)):
        return False
    # Check reasonable range to prevent abuse
    try:
        uid = int(user_id)
        return 1 <= uid <= 999999
    except ValueError:
        return False

@app.route('/user')
def get_user():
    user_id = request.args.get('id')
    
    # Log the access attempt
    logger.info(f"User access attempt for ID: {user_id}")
    
    # Input validation
    if not validate_user_id(user_id):
        logger.warning(f"Invalid user ID attempted: {user_id}")
        return jsonify({'error': 'Invalid user ID format'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Use parameterized query to prevent SQL injection
        query = "SELECT id, name FROM users WHERE id = ?"
        cursor.execute(query, (int(user_id),))
        row = cursor.fetchone()
        
        if row:
            result = {'id': row[0], 'name': row[1]}
            logger.info(f"User found for ID: {user_id}")
            return jsonify(result)
        else:
            logger.info(f"User not found for ID: {user_id}")
            return jsonify({'error': 'User not found'}), 404
            
    except pyodbc.Error as e:
        logger.error(f"Database error for user ID {user_id}: {str(e)}")
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        logger.error(f"Unexpected error for user ID {user_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        if 'conn' in locals():
            conn.close()

# Add security headers
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response

if __name__ == '__main__':
    # Disable debug mode for production
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('PORT', 5000))
    app.run(debug=debug_mode, host='127.0.0.1', port=port)
