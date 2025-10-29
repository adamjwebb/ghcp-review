# Secure Python Flask API for Azure SQL Database

This project is a secure Python API built with Flask that connects to an Azure SQL Database, implementing security best practices and industry standards.

## Security Features

### 🔐 Authentication & Authorization
- Environment-based configuration (no hardcoded credentials)
- Secure credential management using `.env` files
- Secret key management for session security

### 🛡️ Input Validation & Sanitization
- Comprehensive input validation for all user inputs
- Type checking and range validation
- Protection against integer overflow attacks

### 💉 SQL Injection Prevention
- Parameterized queries for all database operations
- No string concatenation in SQL queries
- Proper use of prepared statements

### 🚦 Rate Limiting
- Configurable rate limiting per endpoint
- Protection against brute force attacks
- Configurable limits per minute

### 🔒 Security Headers
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Strict-Transport-Security (HSTS)
- Content-Security-Policy

### 🔍 Logging & Monitoring
- Comprehensive logging of security events
- Error tracking without exposing sensitive data
- Configurable log levels

### 🗄️ Secure Database Connection
- Encrypted connections (TLS/SSL)
- Server certificate validation
- Connection timeout configuration
- Proper connection pooling and cleanup

### ⚠️ Error Handling
- Generic error messages to users (no information disclosure)
- Detailed logging for administrators
- Proper exception handling throughout

## Installation

### Prerequisites
- Python 3.8 or higher
- Azure SQL Database instance
- ODBC Driver 18 for SQL Server

### 1. Clone the repository
```bash
git clone https://github.com/adamjwebb/ghcp-review.git
cd ghcp-review
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment variables
Copy the example environment file and configure it with your Azure SQL Database details:

```bash
cp .env.example .env
```

Edit `.env` and set the following variables:
```bash
DB_SERVER=your-server.database.windows.net
DB_DATABASE=your-database-name
DB_USERNAME=your-username
DB_PASSWORD=your-password
FLASK_SECRET_KEY=your-secret-key-change-this
```

**Important:** Never commit the `.env` file to version control. It's already included in `.gitignore`.

### 4. Run the API
```bash
python app.py
```

The API will start on `http://127.0.0.1:5000`

## API Endpoints

### Health Check
```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "service": "user-api"
}
```

### Get User by ID
```bash
GET /user?id=1
```

Query Parameters:
- `id` (required): User ID (positive integer)

Success Response (200):
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com"
}
```

Error Response (400):
```json
{
  "error": "User ID must be a positive integer"
}
```

Error Response (404):
```json
{
  "error": "User not found"
}
```

Error Response (429):
```json
{
  "error": "Rate limit exceeded. Please try again later."
}
```

## Configuration

The application can be configured using environment variables in the `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_SERVER` | Azure SQL Server hostname | (required) |
| `DB_DATABASE` | Database name | (required) |
| `DB_USERNAME` | Database username | (required) |
| `DB_PASSWORD` | Database password | (required) |
| `DB_DRIVER` | ODBC driver name | `{ODBC Driver 18 for SQL Server}` |
| `FLASK_ENV` | Environment (development/production) | `production` |
| `FLASK_SECRET_KEY` | Secret key for sessions | (required) |
| `RATE_LIMIT_ENABLED` | Enable/disable rate limiting | `true` |
| `RATE_LIMIT_PER_MINUTE` | Requests per minute | `60` |
| `LOG_LEVEL` | Logging level | `INFO` |

## Security Best Practices

### For Developers
1. **Never hardcode credentials** - Always use environment variables
2. **Use parameterized queries** - Prevent SQL injection attacks
3. **Validate all inputs** - Check type, range, and format
4. **Implement rate limiting** - Protect against abuse
5. **Add security headers** - Protect against common web vulnerabilities
6. **Log security events** - Monitor for suspicious activity
7. **Handle errors gracefully** - Don't expose sensitive information
8. **Keep dependencies updated** - Regularly update packages for security patches

### For Deployment
1. Use HTTPS/TLS for all connections
2. Set strong, unique secret keys
3. Enable rate limiting in production
4. Configure appropriate log levels
5. Use connection pooling for better performance
6. Implement database user with minimal required privileges
7. Regularly rotate credentials
8. Monitor logs for security events
9. Keep ODBC drivers and Python packages up to date
10. Use Azure Key Vault or similar for credential management

## Database Schema

The application expects a `users` table with the following structure:

```sql
CREATE TABLE users (
    id INT PRIMARY KEY IDENTITY(1,1),
    username NVARCHAR(100) NOT NULL,
    email NVARCHAR(255) NOT NULL
);
```

## Testing

Example API calls:

```bash
# Health check
curl "http://127.0.0.1:5000/health"

# Get user by ID
curl "http://127.0.0.1:5000/user?id=1"

# Invalid ID (should return 400)
curl "http://127.0.0.1:5000/user?id=abc"

# SQL injection attempt (will be blocked)
curl "http://127.0.0.1:5000/user?id=1%20OR%201=1"
```

## Security Vulnerability Reporting

If you discover a security vulnerability, please report it to the repository maintainers. Do not open public issues for security vulnerabilities.

## License

This project is provided for educational and demonstration purposes.

## Dependencies

- **Flask 3.0.0** - Web framework
- **pyodbc 5.0.1** - Database connectivity
- **python-dotenv 1.0.0** - Environment variable management
- **Flask-Limiter 3.5.0** - Rate limiting
- **Werkzeug 3.0.1** - WSGI utilities

All dependencies are regularly updated to address security vulnerabilities.
