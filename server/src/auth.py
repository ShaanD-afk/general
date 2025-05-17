from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from .db import query_db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    hashed = generate_password_hash(data["password"])
    user_id = query_db(
        "INSERT INTO users (username, password, role, class_id) VALUES (%s, %s, %s, %s) RETURNING id",
        (data["username"], hashed, data["role"], data.get("class_id")),
        one=True,
        commit=True,
    )
    return jsonify({"user_id": user_id}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    user = query_db(
        "SELECT * FROM users WHERE username = %s", (data["username"],), one=True
    )
    if user and check_password_hash(user["password"], data["password"]):
        session["user_id"] = user["id"]
        return jsonify({"message": "Logged in"})
    return jsonify({"error": "Invalid credentials"}), 401


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    return jsonify({"message": "Logged out"})


@auth_bp.route("/me", methods=["GET"])
def me():
    uid = session.get("user_id")
    if not uid:
        return jsonify({"error": "Not logged in"}), 401
    user = query_db(
        "SELECT id, username, role, class_id FROM users WHERE id = %s", (uid,), one=True
    )
    return jsonify(user)
