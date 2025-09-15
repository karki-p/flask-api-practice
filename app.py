from flask import Flask, request, jsonify
import os
import sqlite3
from dotenv import load_dotenv

# Load .env (optional, lets you override DB_PATH)
load_dotenv()

# Location for the SQLite file: default to ./data/app.sqlite
DB_PATH = os.getenv("DB_PATH", "data/app.sqlite")

# Ensure the folder exists (safe even if DB_PATH has no folder)
dir_ = os.path.dirname(DB_PATH)
if dir_:
    os.makedirs(dir_, exist_ok=True)

def get_connection():
    """Return a SQLite connection with safe defaults."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    # Good defaults
    cur.execute("PRAGMA foreign_keys = ON")
    cur.execute("PRAGMA journal_mode = WAL")
    cur.execute("PRAGMA busy_timeout = 3000")  # ms
    cur.close()
    return conn

def init_db():
    """Create the users table if it doesn't exist."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id    INTEGER PRIMARY KEY,
            name  TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            date  TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

app = Flask(__name__)
init_db()

# ---------------- ROUTES ---------------- #

@app.get("/health")
def health():
    """Check DB connection and return version info."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT sqlite_version()")
        version = cur.fetchone()[0]
        return jsonify({
            "status": "ok",
            "engine": "sqlite",
            "version": version,
            "path": os.path.abspath(DB_PATH)
        }), 200
    except sqlite3.Error as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        try:
            conn.close()
        except:
            pass

@app.post("/api/users")
def create_user():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    email = data.get("email")
    date_str = data.get("date")  # "YYYY-MM-DD"

    if not (name and email and date_str):
        return jsonify({"error": "name, email, and date are required"}), 400

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (name, email, date) VALUES (?, ?, ?)",
            (name, email, date_str)
        )
        new_id = cur.lastrowid
        conn.commit()

        cur.execute("SELECT id, name, email, date FROM users WHERE id = ?", (new_id,))
        row = cur.fetchone()
        return jsonify(dict(row)), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email must be unique"}), 409
    finally:
        conn.close()

@app.get("/api/users")
def list_users():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, name, email, date FROM users ORDER BY id")
        rows = cur.fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()

@app.get("/api/users/<int:user_id>")
def get_user(user_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, name, email, date FROM users WHERE id = ?", (user_id,))
        row = cur.fetchone()
        if not row:
            return jsonify({"error": "User not found"}), 404
        return jsonify(dict(row)), 200
    finally:
        conn.close()

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
        cur.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if not cur.fetchone():
            return jsonify({"error": "User not found"}), 404

        cur.execute(
            "UPDATE users SET name = ?, email = ?, date = ? WHERE id = ?",
            (name, email, date_str, user_id)
        )
        conn.commit()

        cur.execute("SELECT id, name, email, date FROM users WHERE id = ?", (user_id,))
        row = cur.fetchone()
        return jsonify(dict(row)), 200
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email must be unique"}), 409
    finally:
        conn.close()

@app.delete("/api/users/<int:user_id>")
def delete_user(user_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if not cur.fetchone():
            return jsonify({"error": "User not found"}), 404

        cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        return jsonify({"message": "Deleted"}), 200
    finally:
        conn.close()

# ---------------- MAIN ---------------- #

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)