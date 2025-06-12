#!/usr/bin/env python3
"""
Security validation tests for the Flask application.
Tests the security measures implemented in app.py.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the current directory to the path to import our app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestSecurity(unittest.TestCase):
    """Test security features of the Flask application."""
    
    def setUp(self):
        """Set up test environment."""
        # Mock Flask and other dependencies since they may not be installed
        self.mock_flask = MagicMock()
        self.mock_request = MagicMock()
        self.mock_jsonify = MagicMock()
        
    def test_input_validation_function(self):
        """Test that input validation function works correctly."""
        # Import our validation function
        from app import validate_user_id
        
        # Test valid inputs
        self.assertTrue(validate_user_id('1'))
        self.assertTrue(validate_user_id('123'))
        
        # Test invalid inputs
        self.assertFalse(validate_user_id(''))
        self.assertFalse(validate_user_id(None))
        self.assertFalse(validate_user_id('abc'))
        self.assertFalse(validate_user_id('0'))
        self.assertFalse(validate_user_id('-1'))
        self.assertFalse(validate_user_id('1; DROP TABLE users'))
        self.assertFalse(validate_user_id("1' OR '1'='1"))
        
    def test_environment_variable_usage(self):
        """Test that environment variables are used for configuration."""
        # Read the app.py file content
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Check that environment variables are used instead of hardcoded values
        self.assertIn('os.getenv', content)
        self.assertIn('DB_SERVER', content)
        self.assertIn('DB_DATABASE', content)
        self.assertIn('DB_USERNAME', content)
        self.assertIn('DB_PASSWORD', content)
        
        # Ensure no hardcoded database credentials
        self.assertNotIn('server = "', content)
        self.assertNotIn('password = "', content)
        
    def test_parameterized_query_usage(self):
        """Test that parameterized queries are used to prevent SQL injection."""
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Check for parameterized query pattern
        self.assertIn('cursor.execute(query, (user_id,))', content)
        self.assertIn('SELECT id, name, email FROM users WHERE id = ?', content)
        
        # Ensure no string concatenation in SQL queries
        self.assertNotIn('f"SELECT', content.replace('f"Database', ''))  # Exclude log messages
        
    def test_security_headers(self):
        """Test that security headers are implemented."""
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Check for security headers
        self.assertIn('X-Content-Type-Options', content)
        self.assertIn('X-Frame-Options', content)
        self.assertIn('X-XSS-Protection', content)
        self.assertIn('Strict-Transport-Security', content)
        
    def test_error_handling(self):
        """Test that proper error handling is implemented."""
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Check for error handling patterns
        self.assertIn('try:', content)
        self.assertIn('except', content)
        self.assertIn('finally:', content)
        self.assertIn('app.logger.error', content)
        
    def test_gitignore_security(self):
        """Test that sensitive files are properly ignored."""
        with open('.gitignore', 'r') as f:
            content = f.read()
        
        # Check that .env file is ignored
        self.assertIn('.env', content)
        self.assertIn('*.log', content)
        
    def test_env_example_file(self):
        """Test that .env.example exists and doesn't contain real credentials."""
        self.assertTrue(os.path.exists('.env.example'))
        
        with open('.env.example', 'r') as f:
            content = f.read()
        
        # Should contain example values, not real ones
        self.assertIn('your-server.database.windows.net', content)
        self.assertIn('your-database-name', content)
        self.assertIn('your-username', content)
        self.assertIn('your-password', content)

class TestCodeStructure(unittest.TestCase):
    """Test the overall code structure and best practices."""
    
    def test_no_debug_in_production(self):
        """Test that debug mode is controlled by environment."""
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Debug should be controlled by environment
        self.assertIn("os.getenv('FLASK_ENV') != 'production'", content)
        
    def test_import_safety(self):
        """Test that imports are handled safely."""
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Should handle missing pyodbc gracefully
        self.assertIn('try:', content)
        self.assertIn('import pyodbc', content)
        self.assertIn('except ImportError:', content)


if __name__ == '__main__':
    print("Running security validation tests...")
    unittest.main(verbosity=2)