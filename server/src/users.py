from flask import Blueprint, jsonify, request
from .db import query_db
from .utils import hash_password, verify_password

users_bp = Blueprint("users", __name__)


@users_bp.route("/users", methods=["GET"])
def all_users():
    return jsonify(query_db("SELECT id, username, role FROM users"))


@users_bp.route("/users/<int:user_id>", methods=["GET"])
def user_detail(user_id):
    return jsonify(
        query_db(
            "SELECT id, username, role, class_id FROM users WHERE id = %s",
            (user_id,),
            one=True,
        )
    )


@users_bp.route("/users", methods=["POST"])
def create_user():
    data = request.json
    hashed = hash_password(data["password"])
    row = query_db(
        "INSERT INTO users (username, password, role, class_id) VALUES (%s, %s, %s, %s) RETURNING id",
        (data["username"], hashed, data["role"], data.get("class_id")),
        one=True,
        commit=True,
    )
    return jsonify({"id": row["id"]})


@users_bp.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    query_db("DELETE FROM users WHERE id = %s", (user_id,), commit=True)
    return jsonify({"deleted": user_id})
