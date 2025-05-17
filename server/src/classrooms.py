from flask import Blueprint, request, jsonify
from .db import query_db

classrooms_bp = Blueprint("classrooms", __name__)


@classrooms_bp.route("/classrooms", methods=["GET"])
def get_classrooms():
    return jsonify(
        query_db(
            "SELECT classrooms.*, u.username AS professor FROM classrooms JOIN users u ON classrooms.professor_id = u.id"
        )
    )


@classrooms_bp.route("/classrooms/<int:id>", methods=["GET"])
def classroom_detail(id):
    classroom = query_db("SELECT * FROM classrooms WHERE id = %s", (id,), one=True)
    students = query_db(
        "SELECT id, username FROM users WHERE class_id = %s AND role = 'student'", (id,)
    )
    programs = query_db("SELECT id, title FROM programs WHERE class_id = %s", (id,))
    return jsonify({"classroom": classroom, "students": students, "programs": programs})


@classrooms_bp.route("/classrooms", methods=["POST"])
def create_classroom():
    data = request.json
    row = query_db(
        "INSERT INTO classrooms (name, professor_id) VALUES (%s, %s) RETURNING id",
        (data["name"], data["professor_id"]),
        one=True,
        commit=True,
    )
    return jsonify({"id": row["id"]})


@classrooms_bp.route("/classrooms/<int:id>", methods=["DELETE"])
def delete_classroom(id):
    query_db("DELETE FROM classrooms WHERE id = %s", (id,), commit=True)
    return jsonify({"deleted": id})
