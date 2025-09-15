# Complete Flask CRUD API Documentation

## Overview
This is a Flask web application that provides a complete CRUD (Create, Read, Update, Delete) API for managing users in a MySQL database. The application uses environment variabl es for database configuration and includes proper error handling.

---

## Imports and Dependencies (Lines 1-5)

```python
from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
import mysql.connector
from datetime import date
```

**Line 1:** `from flask import Flask, request, jsonify`
- **Flask**: The main web framework class
- **request**: Object that contains all the data sent by the client (headers, body, query parameters)
- **jsonify**: Converts Python dictionaries/lists to JSON response format

**Line 2:** `import os`
- **Purpose**: Access to operating system interface functions
- **Usage**: Used to read environment variables with `os.getenv()`

**Line 3:** `from dotenv import load_dotenv`
- **Purpose**: Loads environment variables from a `.env` file
- **Why**: Keeps sensitive data (like database passwords) out of source code

**Line 4:** `import mysql.connector`
- **Purpose**: MySQL database connector for Python
- **Function**: Enables communication with MySQL database

**Line 5:** `from datetime import date`
- **Purpose**: Import the `date` class for handling date objects
- **Usage**: Converts MySQL date objects to ISO format strings

---

## Environment Configuration (Lines 7-8)

```python
# --- Load settings from .env so we don't hardcode passwords in code ---
load_dotenv()  # looks for a file named ".env" next to this script
```

**Line 7:** Comment explaining the purpose of loading environment variables
**Line 8:** `load_dotenv()`
- **Purpose**: Reads the `.env` file and loads all variables into the environment
- **Security**: Prevents hardcoding sensitive information in the source code
- **File**: Looks for `.env` file in the same directory as the script

---

## Database Connection Function (Lines 10-20)

```python
# --- This function makes a NEW connection to MySQL each time we call it ---
# Baby explanation: "Call this when you need to talk to the database, close it after."
def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "practice_db"),
        autocommit=True  # so we don't need to call conn.commit() after INSERT/UPDATE/DELETE
    )
```

**Line 10-11:** Comments explaining the function's purpose
**Line 12:** `def get_connection():`
- **Purpose**: Creates a new database connection each time it's called
- **Pattern**: "Open connection, use it, close it" - prevents connection leaks

**Line 13:** `return mysql.connector.connect(`
- **Purpose**: Establishes connection to MySQL database
- **Returns**: A connection object that can execute SQL queries

**Line 14:** `host=os.getenv("DB_HOST", "127.0.0.1"),`
- **Purpose**: Gets database host from environment variable
- **Default**: "127.0.0.1" (localhost) if not set in `.env`
- **Environment Variable**: `DB_HOST`

**Line 15:** `port=int(os.getenv("DB_PORT", "3306")),`
- **Purpose**: Gets database port from environment variable
- **Default**: 3306 (MySQL default port)
- **int()**: Converts string to integer (environment variables are always strings)

**Line 16:** `user=os.getenv("DB_USER", "root"),`
- **Purpose**: Gets database username from environment variable
- **Default**: "root" (MySQL default superuser)

**Line 17:** `password=os.getenv("DB_PASSWORD", ""),`
- **Purpose**: Gets database password from environment variable
- **Default**: Empty string (no password)
- **Security**: Password stored in `.env` file, not in code

**Line 18:** `database=os.getenv("DB_NAME", "practice_db"),`
- **Purpose**: Gets database name from environment variable
- **Default**: "practice_db"

**Line 19:** `autocommit=True`
- **Purpose**: Automatically commits transactions after each SQL statement
- **Benefit**: No need to call `conn.commit()` after INSERT/UPDATE/DELETE
- **Trade-off**: Less control over transaction boundaries

---

## Flask Application Initialization (Line 22)

```python
app = Flask(__name__)
```

**Purpose**: Creates the Flask application instance
- **`__name__`**: Tells Flask where to find templates, static files, etc.
- **`app`**: The main application object that handles routing and requests

---

## Health Check Endpoint (Lines 24-41)

```python
# # Health check endpoint
# # Baby: "A doctor check for the app. If OK, it says ok."
@app.get("/health")
def health():
    try:
        conn = get_connection()        # open door to DB
        cur = conn.cursor()            # use a mouthpiece (cursor) to talk to DB
        cur.execute("SELECT DATABASE()")
        which_db = cur.fetchone()[0]   # get the DB name (like 'practice_db')
        return jsonify({"status": "ok", "db": which_db}), 200
    except mysql.connector.Error as e:
        # If something is wrong (e.g., DB down), say "error"
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        try:
            conn.close()               # close the door to DB
        except:
             pass
```

**Line 24-25:** Comments explaining the health check purpose
**Line 26:** `@app.get("/health")`
- **Purpose**: Decorator that creates a GET endpoint at `/health`
- **Usage**: `GET http://localhost:5000/health`

**Line 27:** `def health():`
- **Purpose**: Function that handles health check requests
- **Returns**: JSON response with status and database name

**Line 28:** `try:`
- **Purpose**: Start of error handling block
- **Catches**: Any database connection or query errors

**Line 29:** `conn = get_connection()`
- **Purpose**: Opens a new database connection
- **Comment**: "open door to DB" - establishes communication channel

**Line 30:** `cur = conn.cursor()`
- **Purpose**: Creates a cursor object to execute SQL queries
- **Comment**: "use a mouthpiece" - cursor is the interface for SQL commands

**Line 31:** `cur.execute("SELECT DATABASE()")`
- **Purpose**: Executes SQL query to get current database name
- **SQL**: `SELECT DATABASE()` returns the name of the currently selected database

**Line 32:** `which_db = cur.fetchone()[0]`
- **Purpose**: Gets the first (and only) row from the query result
- **`fetchone()`**: Returns one row as a tuple
- **`[0]`**: Gets the first column (database name)

**Line 33:** `return jsonify({"status": "ok", "db": which_db}), 200`
- **Purpose**: Returns successful response with database name
- **Status Code**: 200 (OK)
- **JSON**: Contains status and database name

**Line 34:** `except mysql.connector.Error as e:`
- **Purpose**: Catches MySQL-specific errors
- **Examples**: Connection refused, invalid credentials, database not found

**Line 35-36:** Comments explaining error handling
**Line 36:** `return jsonify({"status": "error", "message": str(e)}), 500`
- **Purpose**: Returns error response
- **Status Code**: 500 (Internal Server Error)
- **Message**: Converts error to string for JSON response

**Line 37:** `finally:`
- **Purpose**: Code that always runs, whether success or error
- **Usage**: Ensures database connection is closed

**Line 38-41:** Connection cleanup
- **Purpose**: Safely closes database connection
- **`try/except`**: Prevents errors if connection is already closed
- **`pass`**: Do nothing if close() fails

---

## CREATE User Endpoint (Lines 43-80)

```python
# CREATE a user (POST)
# Baby: "We make a new user."
# Send JSON body like:
# { "name": "Paras", "email": "paras@example.com", "date": "2025-09-11" }
@app.post("/api/users")
def create_user():
    data = request.get_json(silent=True) or {}   # take JSON from the request
    name = data.get("name")
    email = data.get("email")
    date_str = data.get("date")  # must be "YYYY-MM-DD" because MySQL DATE

    # If any piece is missing, we say "bad request"
    if not (name and email and date_str):
        return jsonify({"error": "name, email, and date are required"}), 400

    conn = get_connection()
    cur = conn.cursor()
    try:
        # Put the new row into the table
        cur.execute(
            "INSERT INTO users (name, email, date) VALUES (%s, %s, %s)",
            (name, email, date_str)
        )
        new_id = cur.lastrowid  # MySQL gives us the new id

        # Ask DB for the row we just added, so we can show it back
        cur.execute("SELECT id, name, email, date FROM users WHERE id=%s", (new_id,))
        row = cur.fetchone()  # row looks like (id, name, email, date_obj)

        # Turn row into a simple dict for JSON
        # (no helper function, we do it right here)
        d = row[3].isoformat() if isinstance(row[3], date) else row[3]
        return jsonify({"id": row[0], "name": row[1], "email": row[2], "date": d}), 201
    except mysql.connector.errors.IntegrityError:
        # This happens if email is already used (UNIQUE)
        return jsonify({"error": "Email must be unique"}), 409
    finally:
        conn.close()
```

**Line 43-46:** Comments explaining the CREATE operation and example JSON
**Line 47:** `@app.post("/api/users")`
- **Purpose**: Creates POST endpoint for creating users
- **URL**: `POST http://localhost:5000/api/users`

**Line 48:** `def create_user():`
- **Purpose**: Function that handles user creation requests

**Line 49:** `data = request.get_json(silent=True) or {}`
- **Purpose**: Extracts JSON data from the request body
- **`silent=True`**: Returns `None` instead of raising error if JSON is invalid
- **`or {}`**: Uses empty dict if JSON parsing fails

**Line 50-52:** Extract individual fields from JSON
- **Purpose**: Get required fields from the request
- **`data.get()`**: Returns `None` if key doesn't exist (safer than `data["key"]`)

**Line 55-56:** Validation
- **Purpose**: Check if all required fields are present and not empty
- **`and`**: All conditions must be true
- **Status Code**: 400 (Bad Request) for missing fields

**Line 58-59:** Database setup
- **Purpose**: Get connection and cursor for database operations

**Line 60:** `try:`
- **Purpose**: Start error handling for database operations

**Line 62-65:** Insert new user
- **SQL**: `INSERT INTO users (name, email, date) VALUES (%s, %s, %s)`
- **`%s`**: Placeholders for parameterized queries (prevents SQL injection)
- **Tuple**: `(name, email, date_str)` provides values for placeholders

**Line 66:** `new_id = cur.lastrowid`
- **Purpose**: Gets the auto-generated ID of the inserted row
- **MySQL Feature**: `lastrowid` contains the ID of the last inserted row

**Line 68-70:** Retrieve the created user
- **Purpose**: Get the complete user record to return to client
- **`WHERE id=%s`**: Find the user by the ID we just created

**Line 71-72:** Comments about data conversion
**Line 74:** `d = row[3].isoformat() if isinstance(row[3], date) else row[3]`
- **Purpose**: Convert date object to ISO string format
- **`isinstance(row[3], date)`**: Check if the value is a date object
- **`isoformat()`**: Converts date to "YYYY-MM-DD" string
- **`else row[3]`**: Keep as-is if not a date object

**Line 75:** `return jsonify({"id": row[0], "name": row[1], "email": row[2], "date": d}), 201`
- **Purpose**: Return the created user data
- **Status Code**: 201 (Created) - indicates successful resource creation
- **JSON**: Contains all user fields

**Line 76:** `except mysql.connector.errors.IntegrityError:`
- **Purpose**: Catches database constraint violations
- **Example**: Duplicate email (if email column has UNIQUE constraint)

**Line 78:** `return jsonify({"error": "Email must be unique"}), 409`
- **Status Code**: 409 (Conflict) - indicates resource conflict
- **Message**: Explains the constraint violation

**Line 79-80:** Cleanup
- **Purpose**: Always close database connection

---

## READ All Users Endpoint (Lines 82-98)

```python
# READ all users (GET)
# Baby: "Show me the whole list."
@app.get("/api/users")
def list_users():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, name, email, date FROM users ORDER BY id")
        rows = cur.fetchall()  # many rows: [(...), (...)]
        # Convert each row tuple into a small dict
        users = []
        for r in rows:
            d = r[3].isoformat() if isinstance(r[3], date) else r[3]
            users.append({"id": r[0], "name": r[1], "email": r[2], "date": d})
        return jsonify(users), 200
    finally:
        conn.close()
```

**Line 82-83:** Comments explaining the READ operation
**Line 84:** `@app.get("/api/users")`
- **Purpose**: Creates GET endpoint for retrieving all users
- **URL**: `GET http://localhost:5000/api/users`

**Line 85:** `def list_users():`
- **Purpose**: Function that handles listing all users

**Line 86-87:** Database setup
- **Purpose**: Get connection and cursor

**Line 88:** `try:`
- **Purpose**: Start error handling

**Line 89:** `cur.execute("SELECT id, name, email, date FROM users ORDER BY id")`
- **SQL**: Selects all user fields from users table
- **`ORDER BY id`**: Sorts results by ID (ascending order)

**Line 90:** `rows = cur.fetchall()`
- **Purpose**: Gets all rows from the query result
- **Returns**: List of tuples, each tuple is one row
- **Comment**: Shows example format `[(...), (...)]`

**Line 91-92:** Comments about data conversion
**Line 93:** `users = []`
- **Purpose**: Initialize empty list to store converted user data

**Line 94-96:** Convert each row to dictionary
- **Purpose**: Transform database rows into JSON-friendly format
- **Loop**: Process each row tuple
- **Date conversion**: Same logic as in create_user
- **Dictionary**: Create user object with named fields

**Line 97:** `return jsonify(users), 200`
- **Purpose**: Return list of all users
- **Status Code**: 200 (OK)

**Line 98-99:** Cleanup
- **Purpose**: Close database connection

---

## READ Single User Endpoint (Lines 100-115)

```python
# READ one user by ID (GET)
# Baby: "Show me just this one."
# Example: GET /api/users/1
@app.get("/api/users/<int:user_id>")
def get_user(user_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, name, email, date FROM users WHERE id=%s", (user_id,))
        row = cur.fetchone()
        if not row:
            return jsonify({"error": "User not found"}), 404
        d = row[3].isoformat() if isinstance(row[3], date) else row[3]
        return jsonify({"id": row[0], "name": row[1], "email": row[2], "date": d}), 200
    finally:
        conn.close()
```

**Line 100-102:** Comments explaining single user retrieval
**Line 103:** `@app.get("/api/users/<int:user_id>")`
- **Purpose**: Creates GET endpoint with URL parameter
- **`<int:user_id>`**: URL parameter that must be an integer
- **Example**: `GET /api/users/1` → `user_id = 1`

**Line 104:** `def get_user(user_id):`
- **Purpose**: Function that handles single user retrieval
- **Parameter**: `user_id` comes from the URL

**Line 105-106:** Database setup

**Line 107:** `try:`
- **Purpose**: Start error handling

**Line 108:** `cur.execute("SELECT id, name, email, date FROM users WHERE id=%s", (user_id,))`
- **SQL**: Selects user by specific ID
- **`WHERE id=%s`**: Filters by the provided user ID
- **Parameter**: `(user_id,)` - tuple with single value

**Line 109:** `row = cur.fetchone()`
- **Purpose**: Gets one row from the query result
- **Returns**: Tuple if found, `None` if not found

**Line 110-111:** Check if user exists
- **Purpose**: Handle case where user ID doesn't exist
- **Status Code**: 404 (Not Found)

**Line 112-113:** Convert and return user data
- **Purpose**: Same date conversion and JSON response as other endpoints

**Line 114-115:** Cleanup

---

## UPDATE User Endpoint (Lines 117-154)

```python
# UPDATE a user fully (PUT)
# Baby: "Replace the whole user info."
# Send JSON body like:
# { "name": "New Name", "email": "new@example.com", "date": "2025-10-01" }
@app.put("/api/users/<int:user_id>")
def update_user(user_id):
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    email = data.get("email")
    date_str = data.get("date")

    if not (name and email and date_str):
        return jsonify({"error": "name, email, and date are required"}), 400

    conn = get_connection()
    cur = conn.cursor()
    try:
        # First, check if the user exists
        cur.execute("SELECT id FROM users WHERE id=%s", (user_id,))
        exists = cur.fetchone()
        if not exists:
            return jsonify({"error": "User not found"}), 404

        # Now update the row
        cur.execute(
            "UPDATE users SET name=%s, email=%s, date=%s WHERE id=%s",
            (name, email, date_str, user_id)
        )

        # Ask for the updated row
        cur.execute("SELECT id, name, email, date FROM users WHERE id=%s", (user_id,))
        row = cur.fetchone()
        d = row[3].isoformat() if isinstance(row[3], date) else row[3]
        return jsonify({"id": row[0], "name": row[1], "email": row[2], "date": d}), 200
    except mysql.connector.errors.IntegrityError:
        return jsonify({"error": "Email must be unique"}), 409
    finally:
        conn.close()
```

**Line 117-120:** Comments explaining UPDATE operation
**Line 121:** `@app.put("/api/users/<int:user_id>")`
- **Purpose**: Creates PUT endpoint for updating users
- **URL**: `PUT http://localhost:5000/api/users/1`

**Line 122:** `def update_user(user_id):`
- **Purpose**: Function that handles user updates

**Line 123-126:** Extract data from request
- **Purpose**: Same as create_user - get fields from JSON

**Line 128-129:** Validation
- **Purpose**: Ensure all required fields are present

**Line 131-132:** Database setup

**Line 133:** `try:`
- **Purpose**: Start error handling

**Line 134-137:** Check if user exists
- **Purpose**: Verify the user ID exists before updating
- **Query**: Simple SELECT to check existence
- **Status Code**: 404 if user not found

**Line 140-144:** Update the user
- **SQL**: `UPDATE users SET name=%s, email=%s, date=%s WHERE id=%s`
- **Purpose**: Updates all fields for the specified user
- **Parameters**: New values + user ID for WHERE clause

**Line 146-150:** Return updated user
- **Purpose**: Fetch and return the updated user data
- **Same logic**: As create_user for data conversion

**Line 151-152:** Handle integrity errors
- **Purpose**: Catch duplicate email errors

**Line 153-154:** Cleanup

---

## DELETE User Endpoint (Lines 156-174)

```python
# DELETE a user (DELETE)
# Baby: "Throw this one away."
# Example: DELETE /api/users/1
@app.delete("/api/users/<int:user_id>")
def delete_user(user_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Check if the user exists
        cur.execute("SELECT id FROM users WHERE id=%s", (user_id,))
        exists = cur.fetchone()
        if not exists:
            return jsonify({"error": "User not found"}), 404

        # Delete the row
        cur.execute("DELETE FROM users WHERE id=%s", (user_id,))
        return jsonify({"message": "Deleted"}), 200
    finally:
        conn.close()
```

**Line 156-158:** Comments explaining DELETE operation
**Line 159:** `@app.delete("/api/users/<int:user_id>")`
- **Purpose**: Creates DELETE endpoint for removing users
- **URL**: `DELETE http://localhost:5000/api/users/1`

**Line 160:** `def delete_user(user_id):`
- **Purpose**: Function that handles user deletion

**Line 161-162:** Database setup

**Line 163:** `try:`
- **Purpose**: Start error handling

**Line 164-167:** Check if user exists
- **Purpose**: Verify user exists before attempting deletion
- **Status Code**: 404 if user not found

**Line 169-170:** Delete the user
- **SQL**: `DELETE FROM users WHERE id=%s`
- **Purpose**: Removes the user record from database
- **Parameter**: User ID to identify which record to delete

**Line 171:** `return jsonify({"message": "Deleted"}), 200`
- **Purpose**: Confirm successful deletion
- **Status Code**: 200 (OK)
- **Message**: Simple confirmation

**Line 172-173:** Cleanup

---

## Application Startup (Lines 176-177)

```python
if __name__ == "__main__":
    app.run(debug=True)  # debug=True shows helpful errors while learning
```

**Line 176:** `if __name__ == "__main__":`
- **Purpose**: Only run this code when script is executed directly
- **Prevents**: Running when imported as a module

**Line 177:** `app.run(debug=True)`
- **Purpose**: Starts the Flask development server
- **`debug=True`**: Enables debug mode with helpful error messages
- **Default**: Runs on `http://127.0.0.1:5000`

---

## Database Schema Requirements

The application expects a MySQL table with this structure:

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    date DATE NOT NULL
);
```

## Environment Variables (.env file)

Create a `.env` file in the same directory:

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=practice_db
```

## API Endpoints Summary

| Method | URL | Purpose | Status Codes |
|--------|-----|---------|--------------|
| GET | `/health` | Health check | 200, 500 |
| POST | `/api/users` | Create user | 201, 400, 409, 500 |
| GET | `/api/users` | List all users | 200, 500 |
| GET | `/api/users/<id>` | Get single user | 200, 404, 500 |
| PUT | `/api/users/<id>` | Update user | 200, 400, 404, 409, 500 |
| DELETE | `/api/users/<id>` | Delete user | 200, 404, 500 |

This documentation covers every line of the Flask CRUD API, explaining the purpose, functionality, and implementation details of each component.
