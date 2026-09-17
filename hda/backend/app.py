import os
import sqlite3
import datetime
from pathlib import Path

from flask import Flask, g, redirect, render_template, request, session, url_for, send_file, make_response
from flask_session import Session
from werkzeug.security import check_password_hash
from dotenv import load_dotenv

load_dotenv()

BASE_DIR  = Path(__file__).parent
DB_PATH   = BASE_DIR / "app.db"
SEED_PATH = BASE_DIR / "../../shared/seed.sql"
CSS_PATH  = BASE_DIR / "../../shared/styles.css"

STATIC_DIR = BASE_DIR / "../frontend/static"

app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="/static")
app.secret_key = os.environ.get("SECRET_KEY", "dev-hda-secret-change-me")
app.config["SESSION_TYPE"]     = "filesystem"
app.config["SESSION_FILE_DIR"] = str(BASE_DIR / "flask_session")
app.config["SESSION_PERMANENT"] = False
Session(app)

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


@app.before_request
def require_auth():
    if request.path.startswith("/issue-") and not session.get("user_id"):
        if request.headers.get("HX-Request"):
            resp = make_response("", 204)
            resp.headers["HX-Redirect"] = "/login"
            return resp
        return redirect(url_for("login"))


# ── Shared CSS ────────────────────────────────────────────────────────────────

@app.route("/shared/styles.css")
def shared_css():
    return send_file(CSS_PATH, mimetype="text/css")


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    if session.get("user_id"):
        return redirect(url_for("issue_1_xss"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    db   = get_db()
    user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

    if not user or not check_password_hash(user["password_hash"], password):
        return render_template("login.html", error="Wrong credentials"), 401

    session["user_id"]  = user["id"]
    session["username"] = user["username"]
    session["role"]     = user["role"]
    add_log("login", user["username"])
    return redirect(url_for("issue_1_xss"))


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    if request.headers.get("HX-Request"):
        resp = make_response("", 204)
        resp.headers["HX-Redirect"] = "/login"
        return resp
    return redirect(url_for("login"))


@app.route("/issue-1-xss")
def issue_1_xss():
    db       = get_db()
    task     = db.execute("SELECT * FROM tasks WHERE id = 1").fetchone()
    comments = db.execute(
        """SELECT c.id, c.body, c.created_at, u.username
           FROM comments c JOIN users u ON c.user_id = u.id
           WHERE c.task_id = 1 ORDER BY c.created_at ASC""",
    ).fetchall()
    show_secret_notes = (session.get("user_id") == task["owner_id"])
    add_log("page_viewed", session.get("username"), "issue-1-xss")
    return render_template("issue_1_xss.html",
                           username=session.get("username"),
                           task=task,
                           comments=comments,
                           show_secret_notes=show_secret_notes)


@app.route("/comments", methods=["POST"])
def post_comment():
    if not session.get("user_id"):
        return "", 401

    task_id = request.form.get("task_id")
    body    = request.form.get("body", "").strip()
    if not task_id or not body:
        return "", 400

    db = get_db()
    # VULN: xss — body stored raw, no sanitization
    cur = db.execute(
        "INSERT INTO comments (task_id, user_id, body) VALUES (?, ?, ?)",
        (task_id, session["user_id"], body),
    )
    db.commit()

    new_comment = db.execute(
        """SELECT c.id, c.body, c.created_at, u.username
           FROM comments c JOIN users u ON c.user_id = u.id
           WHERE c.id = ?""",
        (cur.lastrowid,),
    ).fetchone()

    add_log("comment_posted", session["username"], f"task {task_id}")

    return render_template("_comment.html", comment=new_comment)


@app.route("/comments-unsafe", methods=["POST"])
def post_comment_unsafe():
    if not session.get("user_id"):
        return "", 401

    task_id = request.form.get("task_id")
    body    = request.form.get("body", "").strip()
    if not task_id or not body:
        return "", 400

    db = get_db()
    # VULN: xss — body stored raw, no sanitization
    cur = db.execute(
        "INSERT INTO comments (task_id, user_id, body) VALUES (?, ?, ?)",
        (task_id, session["user_id"], body),
    )
    db.commit()

    new_comment = db.execute(
        """SELECT c.id, c.body, c.created_at, u.username
           FROM comments c JOIN users u ON c.user_id = u.id
           WHERE c.id = ?""",
        (cur.lastrowid,),
    ).fetchone()

    return render_template("_comment_unsafe.html", comment=new_comment)


@app.route("/issue-2-client-storage")
def issue_2_client_storage():
    db       = get_db()
    task     = db.execute("SELECT * FROM tasks WHERE id = 7").fetchone()
    comments = db.execute(
        """SELECT c.id, c.body, c.created_at, u.username
           FROM comments c JOIN users u ON c.user_id = u.id
           WHERE c.task_id = 7 ORDER BY c.created_at ASC""",
    ).fetchall()
    show_secret_notes = (session.get("user_id") == task["owner_id"])
    add_log("page_viewed", session.get("username"), "issue-2-client-storage")
    return render_template("issue_2_client_storage.html",
                           username=session.get("username"),
                           task=task,
                           comments=comments,
                           show_secret_notes=show_secret_notes)


@app.route("/issue-3-third-party")
def issue_3_third_party():
    add_log("page_viewed", session.get("username"), "issue-3-third-party")
    return render_template("issue_3_third_party.html", username=session.get("username"))


@app.route("/issue-4-monitoring")
def issue_4_monitoring():
    db   = get_db()
    task = db.execute("SELECT * FROM tasks WHERE id = 4").fetchone()
    add_log("page_viewed", session.get("username"), "issue-4-monitoring")
    return render_template("issue_4_monitoring.html",
                           username=session.get("username"),
                           task=task)


@app.route("/logs")
def get_logs():
    rows = ""
    for entry in reversed(activity_log):
        rows += (
            f"<tr>"
            f"<td style='padding:4px 8px;font-size:12px'>{entry['time']}</td>"
            f"<td style='padding:4px 8px;font-size:12px'>{entry['event']}</td>"
            f"<td style='padding:4px 8px;font-size:12px'>{entry['username']}</td>"
            f"<td style='padding:4px 8px;font-size:12px'>{entry['detail']}</td>"
            f"</tr>"
        )
    if not rows:
        rows = "<tr><td colspan='4' style='padding:8px;font-size:12px;color:var(--text-muted)'>No log entries yet.</td></tr>"
    return rows


@app.route("/issue-4-monitoring/add-task", methods=["POST"])
def issue_4_add_task():
    if not session.get("user_id"):
        return "", 401

    title = request.form.get("title", "").strip()
    if not title:
        return "<p style='color:var(--danger-text);font-size:13px'>Title is required.</p>"

    db = get_db()
    cur = db.execute(
        "INSERT INTO tasks (owner_id, title) VALUES (?, ?)",
        (session["user_id"], title),
    )
    db.commit()

    new_task = db.execute("SELECT * FROM tasks WHERE id = ?", (cur.lastrowid,)).fetchone()
    add_log("task_created", session["username"], f"task {new_task['id']}")

    created_at = datetime.datetime.strptime(new_task["created_at"], "%Y-%m-%d %H:%M:%S")
    now = datetime.datetime.now()
    # VULN: deliberate off-by-one bug, produces -1 for tasks created today
    days_since = (now - created_at).days - 1

    if days_since < 0:
        add_log("bug_warning", session["username"], f"days_since_creation={days_since} for task {new_task['id']}")

    return (
        f"<div style='margin-top:10px'>"
        f"<p style='font-size:13px'><strong>Created:</strong> {new_task['title']}</p>"
        f"<p style='font-size:13px'><strong>created_at:</strong> {new_task['created_at']}</p>"
        f"<p style='font-size:13px'><strong>Days since creation:</strong> "
        f"<span style='color:{'var(--danger-text)' if days_since < 0 else 'inherit'};font-weight:600'>{days_since}</span></p>"
        f"</div>"
    )


@app.route("/issue-5-business-logic")
def issue_5_business_logic():
    db   = get_db()
    task = db.execute("SELECT * FROM tasks WHERE id = 8").fetchone()
    add_log("page_viewed", session.get("username"), "issue-5-business-logic")
    return render_template("issue_5_business_logic.html", username=session.get("username"), task=task)


@app.route("/tasks/<int:task_id>/status", methods=["POST"])
def update_task_status(task_id):
    if not session.get("user_id"):
        return "", 401

    new_status = request.form.get("status")
    if new_status not in ("open", "in_progress", "done"):
        return "<p style='color:var(--danger-text);font-size:13px'>Invalid status.</p>", 400

    db   = get_db()
    task = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if not task:
        return "<p style='color:var(--danger-text);font-size:13px'>Task not found.</p>", 404

    if task["status"] == "done" and new_status == "in_progress":
        return "<p style='color:var(--danger-text);font-size:13px'>A completed task cannot be moved back to In Progress.</p>", 400

    db.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id))
    db.commit()
    task = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return render_template("_task_status.html", task=task)


if __name__ == "__main__":
    init_db()
    app.run(port=5002, debug=True)
