# Python Flask API for Azure SQL Database (Intentionally Insecure)

This project is a simple Python API built with Flask that connects to an Azure SQL Database. The code is intentionally unoptimized and contains common security issues for demonstration and educational purposes only.

## Features
- Connects to an Azure SQL Database using hardcoded credentials
- Provides a `/user` endpoint to fetch user data by ID
- Demonstrates SQL injection vulnerability and lack of input validation

## Usage

### 1. Install dependencies
```
pip install -r requirements.txt
```

### 2. Configure Database Connection
Edit `app.py` and replace the following variables with your Azure SQL Database details:
- `server`
- `database`
- `username`
- `password`

### 3. Run the API
```
python app.py
```

### 4. Query the API
Example:
```
curl "http://127.0.0.1:5000/user?id=1"
```

## Security Issues (Intentionally Included)
- Hardcoded database credentials
- No input validation or sanitization
- SQL injection vulnerability
- No error handling for database connection issues

**Do not use this code in production. It is for demonstration purposes only.**
