import json
from flask import Blueprint, request, jsonify
from .db import query_db

quiz_bp = Blueprint("quiz", __name__)


# Mark answers for a quiz and auto-grade
@quiz_bp.route("/quiz/mark", methods=["POST"])
def mark_answers():
    """
    Expects: {
        "quiz_id": int,
        "answers": dict (user answers, e.g. {"0": "B", ...})
    }
    Grades the quiz using the stored answer key and updates marks.
    """
    data = request.json
    quiz_id = data.get("quiz_id")
    user_answers = data.get("answers")

    quiz_row = query_db(
        "SELECT answers, questions FROM quizzes WHERE id = %s",
        (quiz_id,),
        one=True,
    )
    if not quiz_row:
        return jsonify({"error": "Quiz not found"}), 404

    answer_key = json.loads(quiz_row["answers"])
    questions = quiz_row["questions"]
    marks = 0
    total = 0

    # Both answer_key and user_answers are dicts with string indices as keys
    if isinstance(answer_key, dict) and isinstance(user_answers, dict):
        for k, correct in answer_key.items():
            total += 1
            user_val = user_answers.get(k)
            if (
                user_val is not None
                and str(user_val).strip().upper() == str(correct).strip().upper()
            ):
                marks += 1
    else:
        return jsonify({"error": "Invalid answer format"}), 400

    # Update answers and marks in DB
    query_db(
        "UPDATE quizzes SET answers = %s, marks = %s WHERE id = %s RETURNING answers",
        (json.dumps(user_answers), marks, quiz_id),
        commit=True,
    )
    return jsonify({"quiz_id": quiz_id, "marks": marks, "total": total})


# View quizzes by class
@quiz_bp.route("/quiz/class/<int:class_id>", methods=["GET"])
def quizzes_by_class(class_id):
    quizzes = query_db(
        "SELECT * FROM quizzes WHERE class_id = %s",
        (class_id,),
    )
    return jsonify(quizzes)


# View quizzes by program
@quiz_bp.route("/quiz/program/<int:program_id>", methods=["GET"])
def quizzes_by_program(program_id):
    quizzes = query_db(
        """
        SELECT quizzes.*, users.username
        FROM quizzes
        JOIN users ON quizzes.student_id = users.id
        WHERE quizzes.program_id = %s
        """,
        (program_id,),
    )
    return jsonify(quizzes)


# View quiz by program and user id
@quiz_bp.route("/quiz/program/<int:program_id>/user/<int:user_id>", methods=["GET"])
def quiz_by_program_user(program_id, user_id):
    quiz = query_db(
        "SELECT * FROM quizzes WHERE program_id = %s AND student_id = %s",
        (program_id, user_id),
        one=True,
    )
    if not quiz:
        return jsonify({"error": "Quiz not found"}), 404
    return jsonify(quiz)


# View quiz by user id, joining programs table
@quiz_bp.route("/quiz/user/<int:user_id>", methods=["GET"])
def quiz_by_user(user_id):
    quiz = query_db(
        """
        SELECT quizzes.*, programs.title AS program_name
        FROM quizzes
        JOIN programs ON quizzes.program_id = programs.id
        WHERE quizzes.student_id = %s
        """,
        (user_id,),
        one=True,
    )
    if not quiz:
        return jsonify({"error": "Quiz not found"}), 404
    return jsonify(quiz)
