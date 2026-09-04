import os
import sqlite3
import datetime
from pathlib import Path

import jwt
from apiflask import APIFlask
from flask import g, request, jsonify
from flask_cors import CORS
from werkzeug.security import check_password_hash
from dotenv import load_dotenv

load_dotenv()

app = APIFlask(__name__, title="SPA Task Tracker API", version="1.0")
CORS(app, origins=["http://localhost:5173"])

BASE_DIR   = Path(__file__).parent
DB_PATH    = BASE_DIR / "app.db"
SEED_PATH  = BASE_DIR / "../../shared/seed.sql"
JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret-change-me")


def init_db():
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SEED_PATH.read_text())
    conn.commit()
    conn.close()


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_):
    db = g.pop("db", None)
    if db:
        db.close()


@app.post("/api/login")
def login():
    data = request.get_json(force=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    db   = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Wrong credentials"}), 401

    token = jwt.encode(
        {
            "sub":      str(user["id"]),
            "username": user["username"],
            "role":     user["role"],
            "exp":      datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=8),
        },
        JWT_SECRET,
        algorithm="HS256",
    )

    return jsonify({"token": token, "username": user["username"], "role": user["role"]})


def get_current_user():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    try:
        payload = jwt.decode(auth[7:], JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.PyJWTError:
        return None


@app.get("/api/tasks/<int:task_id>")
def get_task(task_id):
    db   = get_db()
    task = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if not task:
        return jsonify({"error": "Not found"}), 404

    comments = db.execute(
        """SELECT c.id, c.body, c.created_at, u.username
           FROM comments c JOIN users u ON c.user_id = u.id
           WHERE c.task_id = ? ORDER BY c.created_at ASC""",
        (task_id,),
    ).fetchall()

    user          = get_current_user()
    current_user_id = int(user["sub"]) if user else None
    secret_notes  = task["secret_notes"] if current_user_id == task["owner_id"] else None

    return jsonify({
        "id":           task["id"],
        "title":        task["title"],
        "description":  task["description"],
        "status":       task["status"],
        "priority":     task["priority"],
        "secret_notes": secret_notes,
        "comments": [
            {"id": c["id"], "body": c["body"], "username": c["username"], "created_at": c["created_at"]}
            for c in comments
        ],
    })


@app.post("/api/comments")
def post_comment():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    data    = request.get_json(force=True) or {}
    task_id = data.get("task_id")
    body    = data.get("body", "").strip()
    if not task_id or not body:
        return jsonify({"error": "task_id and body required"}), 400

    db = get_db()
    # VULN: xss — body stored raw, no sanitization
    cur = db.execute(
        "INSERT INTO comments (task_id, user_id, body) VALUES (?, ?, ?)",
        (task_id, user["sub"], body),
    )
    db.commit()

    new_comment = db.execute(
        """SELECT c.id, c.body, c.created_at, u.username
           FROM comments c JOIN users u ON c.user_id = u.id
           WHERE c.id = ?""",
        (cur.lastrowid,),
    ).fetchone()

    return jsonify({
        "id":         new_comment["id"],
        "body":       new_comment["body"],
        "username":   new_comment["username"],
        "created_at": new_comment["created_at"],
    }), 201


if __name__ == "__main__":
    init_db()
    app.run(port=5001, debug=True)
