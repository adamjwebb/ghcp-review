#!/usr/bin/env python3
"""
Standalone validation function test.
Tests the input validation logic without requiring Flask.
"""

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

def test_validation():
    """Test the validation function."""
    print("Testing input validation function...")
    
    # Test valid inputs
    assert validate_user_id('1') == True, "Should accept '1'"
    assert validate_user_id('123') == True, "Should accept '123'"
    print("✓ Valid inputs accepted")
    
    # Test invalid inputs
    assert validate_user_id('') == False, "Should reject empty string"
    assert validate_user_id(None) == False, "Should reject None"
    assert validate_user_id('abc') == False, "Should reject non-numeric"
    assert validate_user_id('0') == False, "Should reject zero"
    assert validate_user_id('-1') == False, "Should reject negative"
    assert validate_user_id('1; DROP TABLE users') == False, "Should reject SQL injection attempt"
    assert validate_user_id("1' OR '1'='1") == False, "Should reject SQL injection attempt"
    print("✓ Invalid inputs rejected")
    
    print("✓ All validation tests passed!")

if __name__ == '__main__':
    test_validation()