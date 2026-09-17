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

activity_log = []


def add_log(event, username, detail=""):
    activity_log.append({
        "time": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "event": event,
        "username": username,
        "detail": detail,
    })
    if len(activity_log) > 200:
        activity_log.pop(0)


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

    add_log("login", user["username"])
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

    add_log("task_fetched", user["username"] if user else "anonymous", f"task {task_id}")

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

    add_log("comment_posted", user["username"], f"task {task_id}")

    return jsonify({
        "id":         new_comment["id"],
        "body":       new_comment["body"],
        "username":   new_comment["username"],
        "created_at": new_comment["created_at"],
    }), 201


@app.get("/api/logs")
def get_logs():
    return jsonify(activity_log)


@app.post("/api/tasks")
def create_task():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    data  = request.get_json(force=True) or {}
    title = data.get("title", "").strip()
    if not title:
        return jsonify({"error": "title required"}), 400

    db = get_db()
    cur = db.execute(
        "INSERT INTO tasks (owner_id, title) VALUES (?, ?)",
        (user["sub"], title),
    )
    db.commit()

    new_task = db.execute("SELECT * FROM tasks WHERE id = ?", (cur.lastrowid,)).fetchone()
    add_log("task_created", user["username"], f"task {new_task['id']}")

    return jsonify({
        "id":         new_task["id"],
        "title":      new_task["title"],
        "status":     new_task["status"],
        "priority":   new_task["priority"],
        "created_at": new_task["created_at"],
    }), 201


@app.patch("/api/tasks/<int:task_id>/status")
def update_task_status(task_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    data       = request.get_json(force=True) or {}
    new_status = data.get("status")
    if new_status not in ("open", "in_progress", "done"):
        return jsonify({"error": "invalid status"}), 400

    # No guard here — done->in_progress is intentionally allowed by the server
    db = get_db()
    db.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id))
    db.commit()
    task = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return jsonify({"id": task["id"], "status": task["status"]}), 200


if __name__ == "__main__":
    init_db()
    app.run(port=5001, debug=True)
