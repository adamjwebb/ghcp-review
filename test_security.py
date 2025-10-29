"""
Security tests for the Flask API
Tests input validation, SQL injection prevention, and other security features
"""

import unittest
from app import validate_user_id, app


class TestInputValidation(unittest.TestCase):
    """Test input validation functions"""
    
    def test_valid_user_id(self):
        """Test valid user ID"""
        is_valid, sanitized, error = validate_user_id("123")
        self.assertTrue(is_valid)
        self.assertEqual(sanitized, 123)
        self.assertIsNone(error)
    
    def test_empty_user_id(self):
        """Test empty user ID"""
        is_valid, sanitized, error = validate_user_id("")
        self.assertFalse(is_valid)
        self.assertIsNone(sanitized)
        self.assertEqual(error, "User ID is required")
    
    def test_non_numeric_user_id(self):
        """Test non-numeric user ID"""
        is_valid, sanitized, error = validate_user_id("abc")
        self.assertFalse(is_valid)
        self.assertIsNone(sanitized)
        self.assertEqual(error, "User ID must be a positive integer")
    
    def test_sql_injection_attempt(self):
        """Test SQL injection attempt is blocked"""
        is_valid, sanitized, error = validate_user_id("1 OR 1=1")
        self.assertFalse(is_valid)
        self.assertIsNone(sanitized)
        self.assertEqual(error, "User ID must be a positive integer")
    
    def test_negative_user_id(self):
        """Test negative user ID"""
        is_valid, sanitized, error = validate_user_id("-1")
        self.assertFalse(is_valid)
        self.assertIsNone(sanitized)
        self.assertEqual(error, "User ID must be a positive integer")
    
    def test_zero_user_id(self):
        """Test zero user ID"""
        is_valid, sanitized, error = validate_user_id("0")
        self.assertFalse(is_valid)
        self.assertIsNone(sanitized)
        self.assertEqual(error, "User ID must be greater than 0")
    
    def test_large_user_id(self):
        """Test user ID exceeds SQL Server INT max"""
        is_valid, sanitized, error = validate_user_id("2147483648")
        self.assertFalse(is_valid)
        self.assertIsNone(sanitized)
        self.assertEqual(error, "User ID is too large")
    
    def test_float_user_id(self):
        """Test float user ID"""
        is_valid, sanitized, error = validate_user_id("123.45")
        self.assertFalse(is_valid)
        self.assertIsNone(sanitized)
        self.assertEqual(error, "User ID must be a positive integer")
    
    def test_special_characters(self):
        """Test special characters in user ID"""
        is_valid, sanitized, error = validate_user_id("123; DROP TABLE users;")
        self.assertFalse(is_valid)
        self.assertIsNone(sanitized)
        self.assertEqual(error, "User ID must be a positive integer")


class TestSecurityHeaders(unittest.TestCase):
    """Test security headers are applied"""
    
    def setUp(self):
        """Set up test client"""
        self.client = app.test_client()
        self.client.testing = True
    
    def test_security_headers_present(self):
        """Test that security headers are present in response"""
        response = self.client.get('/health')
        
        # Check security headers
        self.assertEqual(response.headers.get('X-Content-Type-Options'), 'nosniff')
        self.assertEqual(response.headers.get('X-Frame-Options'), 'DENY')
        self.assertEqual(response.headers.get('X-XSS-Protection'), '1; mode=block')
        self.assertIn('max-age=31536000', response.headers.get('Strict-Transport-Security', ''))
        self.assertIn("default-src 'self'", response.headers.get('Content-Security-Policy', ''))
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['service'], 'user-api')


class TestErrorHandling(unittest.TestCase):
    """Test error handling"""
    
    def setUp(self):
        """Set up test client"""
        self.client = app.test_client()
        self.client.testing = True
    
    def test_404_error(self):
        """Test 404 error handling"""
        response = self.client.get('/nonexistent')
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertIn('error', data)
    
    def test_invalid_user_id_returns_400(self):
        """Test that invalid user ID returns 400"""
        response = self.client.get('/user?id=invalid')
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)


if __name__ == '__main__':
    unittest.main()
