from flask import Flask, request, jsonify
import pyodbc

app = Flask(__name__)

# Hardcoded credentials (security issue)
server = 'your-azure-sql-server.database.windows.net'
database = 'your-database'
username = 'your-username'
password = 'your-password'
driver= '{ODBC Driver 17 for SQL Server}'

def get_db_connection():
    conn = pyodbc.connect(
        f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    )
    return conn

@app.route('/user')
def get_user():
    user_id = request.args.get('id')  # No input validation (security issue)
    conn = get_db_connection()
    cursor = conn.cursor()
    # SQL injection vulnerability
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    row = cursor.fetchone()
    conn.close()
    if row:
        return jsonify({'id': row[0], 'name': row[1]})
    else:
        return jsonify({'error': 'User not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
