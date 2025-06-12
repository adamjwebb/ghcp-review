import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Try to import pyodbc, but handle gracefully if not available
try:
    import pyodbc
    PYODBC_AVAILABLE = True
except ImportError:
    PYODBC_AVAILABLE = False
    print("Warning: pyodbc not available. Database functionality will be simulated.")

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Database configuration using environment variables (secure approach)
server = os.getenv('DB_SERVER', 'your-server.database.windows.net')
database = os.getenv('DB_DATABASE', 'your-database')
username = os.getenv('DB_USERNAME', 'your-username')
password = os.getenv('DB_PASSWORD', 'your-password')
driver = '{ODBC Driver 17 for SQL Server}'

def get_db_connection():
    """Get database connection with proper error handling."""
    if not PYODBC_AVAILABLE:
        # Return None to simulate database unavailability for demo purposes
        app.logger.warning("Database connection simulated - pyodbc not available")
        return None
        
    try:
        connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
        connection = pyodbc.connect(connection_string)
        return connection
    except pyodbc.Error as e:
        app.logger.error(f"Database connection error: {e}")
        return None

def validate_user_id(user_id):
    """Validate user ID input to prevent injection attacks."""
    if not user_id:
        return False
    try:
        # Ensure user_id is a positive integer
        user_id_int = int(user_id)
        if user_id_int <= 0:
            return False
        return True
    except ValueError:
        return False

@app.route('/user', methods=['GET'])
def get_user():
    """Get user data by ID with proper security measures."""
    user_id = request.args.get('id')
    
    # Input validation
    if not validate_user_id(user_id):
        return jsonify({'error': 'Invalid user ID. Must be a positive integer.'}), 400
    
    # For demonstration purposes when database is not available
    if not PYODBC_AVAILABLE:
        # Simulate database response with sample data
        sample_users = {
            '1': {'id': 1, 'name': 'John Doe', 'email': 'john.doe@example.com'},
            '2': {'id': 2, 'name': 'Jane Smith', 'email': 'jane.smith@example.com'},
            '3': {'id': 3, 'name': 'Bob Johnson', 'email': 'bob.johnson@example.com'}
        }
        
        if user_id in sample_users:
            return jsonify(sample_users[user_id]), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    
    # Get database connection
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor()
        
        # Use parameterized query to prevent SQL injection
        query = "SELECT id, name, email FROM users WHERE id = ?"
        cursor.execute(query, (user_id,))
        
        user = cursor.fetchone()
        
        if user:
            user_data = {
                'id': user[0],
                'name': user[1],
                'email': user[2]
            }
            return jsonify(user_data), 200
        else:
            return jsonify({'error': 'User not found'}), 404
            
    except pyodbc.Error as e:
        app.logger.error(f"Database query error: {e}")
        return jsonify({'error': 'Database query failed'}), 500
    finally:
        connection.close()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'}), 200

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Add security headers
    @app.after_request
    def add_security_headers(response):
        # Prevent XSS attacks
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        # Enforce HTTPS in production
        if os.getenv('FLASK_ENV') == 'production':
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response
    
    # Run with debug mode disabled in production
    debug_mode = os.getenv('FLASK_ENV') != 'production'
    app.run(host='127.0.0.1', port=5000, debug=debug_mode)