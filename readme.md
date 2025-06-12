# Python Flask API for Azure SQL Database (Secure Implementation)

This project is a secure Python API built with Flask that connects to an Azure SQL Database. The code follows security best practices and demonstrates proper implementation of security measures.

## Features
- Securely connects to an Azure SQL Database using environment variables
- Provides a `/user` endpoint to fetch user data by ID with proper validation
- Implements SQL injection protection using parameterized queries
- Includes comprehensive input validation and error handling
- Adds security headers to prevent common web vulnerabilities

## Security Features Implemented
- **Environment-based configuration**: Database credentials stored in environment variables
- **Input validation**: Comprehensive validation of user inputs
- **SQL injection protection**: Parameterized queries prevent SQL injection attacks
- **Error handling**: Proper error handling for database connections and queries
- **Security headers**: X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, and HTTPS enforcement
- **Logging**: Error logging for debugging and monitoring

## Usage

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Database Connection
Copy the example environment file and configure your Azure SQL Database details:
```bash
cp .env.example .env
```
Edit `.env` and replace with your actual Azure SQL Database credentials:
- `DB_SERVER`: Your Azure SQL Server name
- `DB_DATABASE`: Your database name
- `DB_USERNAME`: Your database username
- `DB_PASSWORD`: Your database password
- `FLASK_ENV`: Set to 'production' for production deployment

### 3. Run the API
```bash
python app.py
```

### 4. Query the API
Example:
```bash
# Get user by ID
curl "http://127.0.0.1:5000/user?id=1"

# Health check
curl "http://127.0.0.1:5000/health"
```

## API Endpoints

### GET /user
Fetch user data by ID.

**Parameters:**
- `id` (required): User ID (must be a positive integer)

**Response:**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john.doe@example.com"
}
```

**Error Response:**
```json
{
  "error": "Invalid user ID. Must be a positive integer."
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

## Security Best Practices Implemented

1. **Environment Variables**: Sensitive configuration data is stored in environment variables, not hardcoded
2. **Input Validation**: All user inputs are validated before processing
3. **Parameterized Queries**: SQL queries use parameters to prevent injection attacks
4. **Error Handling**: Comprehensive error handling with appropriate HTTP status codes
5. **Security Headers**: HTTP security headers are added to prevent common attacks
6. **Connection Management**: Database connections are properly opened and closed
7. **Logging**: Errors are logged for monitoring and debugging

**This code follows security best practices and is suitable for production use.**
