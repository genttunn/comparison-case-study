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
            "sub":      user["id"],
            "username": user["username"],
            "role":     user["role"],
            "exp":      datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=8),
        },
        JWT_SECRET,
        algorithm="HS256",
    )

    return jsonify({"token": token, "username": user["username"], "role": user["role"]})


if __name__ == "__main__":
    init_db()
    app.run(port=5001, debug=True)
