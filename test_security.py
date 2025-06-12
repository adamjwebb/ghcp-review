import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add the parent directory to sys.path to import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, validate_user_id

class TestSecurityFixes(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_validate_user_id_valid(self):
        """Test that valid user IDs pass validation"""
        self.assertTrue(validate_user_id('1'))
        self.assertTrue(validate_user_id('123'))
        self.assertTrue(validate_user_id('999999'))

    def test_validate_user_id_invalid(self):
        """Test that invalid user IDs fail validation"""
        # Test empty/None values
        self.assertFalse(validate_user_id(''))
        self.assertFalse(validate_user_id(None))
        
        # Test SQL injection attempts
        self.assertFalse(validate_user_id("1; DROP TABLE users;"))
        self.assertFalse(validate_user_id("1' OR '1'='1"))
        self.assertFalse(validate_user_id("1 UNION SELECT * FROM users"))
        
        # Test non-numeric values
        self.assertFalse(validate_user_id('abc'))
        self.assertFalse(validate_user_id('1a'))
        self.assertFalse(validate_user_id('-1'))
        
        # Test out of range values
        self.assertFalse(validate_user_id('0'))
        self.assertFalse(validate_user_id('1000000'))

    def test_invalid_user_id_returns_400(self):
        """Test that invalid user IDs return HTTP 400"""
        # Test with SQL injection attempt
        response = self.app.get('/user?id=1;DROP TABLE users;')
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data['error'], 'Invalid user ID format')
        
        # Test with non-numeric value
        response = self.app.get('/user?id=abc')
        self.assertEqual(response.status_code, 400)

    def test_missing_user_id_returns_400(self):
        """Test that missing user ID returns HTTP 400"""
        response = self.app.get('/user')
        self.assertEqual(response.status_code, 400)

    def test_security_headers_present(self):
        """Test that security headers are present in response"""
        with patch('app.get_db_connection') as mock_conn:
            # Mock database connection to avoid actual DB calls
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = None
            mock_conn.return_value.cursor.return_value = mock_cursor
            
            response = self.app.get('/user?id=1')
            
            # Test security headers
            self.assertEqual(response.headers.get('X-Content-Type-Options'), 'nosniff')
            self.assertEqual(response.headers.get('X-Frame-Options'), 'DENY')
            self.assertEqual(response.headers.get('X-XSS-Protection'), '1; mode=block')
            self.assertIn('max-age=31536000', response.headers.get('Strict-Transport-Security', ''))
            self.assertEqual(response.headers.get('Content-Security-Policy'), "default-src 'self'")

    @patch('app.get_db_connection')
    def test_database_error_handling(self, mock_conn):
        """Test that database errors are handled properly"""
        # Mock database connection error
        mock_conn.side_effect = Exception("Database connection failed")
        
        response = self.app.get('/user?id=1')
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertEqual(data['error'], 'Internal server error')

if __name__ == '__main__':
    unittest.main()