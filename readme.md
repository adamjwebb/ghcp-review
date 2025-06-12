# Python Flask API for Azure SQL Database (Security Hardened)

This project is a Python API built with Flask that securely connects to an Azure SQL Database. The code has been hardened against common security vulnerabilities and follows security best practices.

## Features
- Securely connects to Azure SQL Database using environment variables for credentials
- Provides a `/user` endpoint to fetch user data by ID with proper input validation
- Implements parameterized queries to prevent SQL injection attacks
- Includes comprehensive input validation and sanitization
- Features proper error handling and security logging
- Implements security headers for defense in depth

## Usage

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Database Connection
Copy `.env.example` to `.env` and update with your Azure SQL Database details:
```bash
cp .env.example .env
```
Then edit `.env` with your actual database credentials:
- `DB_SERVER` - Your Azure SQL server hostname
- `DB_DATABASE` - Your database name  
- `DB_USERNAME` - Your database username
- `DB_PASSWORD` - Your database password
- `DB_DRIVER` - ODBC driver (default is fine for most cases)

### 3. Run the API
```bash
python app.py
```

### 4. Query the API
Example:
```bash
curl "http://127.0.0.1:5000/user?id=1"
```

### 5. Run Security Tests
```bash
python test_security.py
```

## Security Features (Implemented)
- **Environment-based configuration**: Database credentials stored in environment variables
- **Input validation**: Comprehensive validation of all user inputs
- **Parameterized queries**: SQL injection prevention using parameterized queries
- **Error handling**: Proper exception handling with secure error messages
- **Security headers**: Implementation of security headers (HSTS, CSP, etc.)
- **Logging**: Security event logging for monitoring and debugging
- **Production hardening**: Debug mode disabled by default with configurable settings
