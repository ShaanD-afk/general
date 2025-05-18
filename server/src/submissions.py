import json
from flask import Blueprint, request, jsonify
from .db import query_db
from .judge import judge
from .ai import generate_quiz

submissions_bp = Blueprint("submissions", __name__)


@submissions_bp.route("/submissions/program/<int:pid>/user/<int:uid>", methods=["GET"])
def submission_for_program_user(pid, uid):
    return jsonify(
        query_db(
            "SELECT * FROM submissions WHERE program_id = %s AND student_id = %s",
            (pid, uid),
        )
    )


@submissions_bp.route("/submissions/user/<int:uid>", methods=["GET"])
def user_submissions(uid):
    return jsonify(query_db("SELECT * FROM submissions WHERE student_id = %s", (uid,)))


languages = {
    "en": "English",
    "ka": "Kannada",
    "fr": "French",
    "de": "German",
}


@submissions_bp.route("/submissions", methods=["POST"])
def submit_code():
    data = request.json

    prog_row = query_db(
        "SELECT code FROM programs WHERE id = %s", (data["program_id"],), one=True
    )
    if not prog_row:
        return jsonify({"error": "Program not found"}), 404
    actual_code = prog_row["code"]

    # Generate a quiz using the AI function
    quiz_res = generate_quiz(
        data["code"],
        actual_code=actual_code,
        language=languages[data.get("quiz_language", "en")],
    )
    print(quiz_res)
    quiz_json = json.loads(quiz_res)

    code_correct = quiz_json.get("code_correct", True)
    code_errors = quiz_json.get("code_errors", [])
    test_inputs = quiz_json.get("test_inputs", [])
    quiz = quiz_json.get("quiz", [])
    answer_key = quiz_json.get("answer_key", {})

    final_results = []
    for input in test_inputs:
        results = judge(code=data["code"], input=input, language=data["language_id"])
        final_results.append(
            {
                "stdin": input,
                "stdout": results.get("stdout", ""),
                "stderr": results.get("stderr", ""),
                "compile_output": results.get("compile_output", ""),
            }
        )

    quiz_insert = query_db(
        "INSERT INTO quizzes (program_id, student_id, questions, answers) VALUES (%s, %s, %s, %s) RETURNING id",
        (
            data["program_id"],
            data["user_id"],
            json.dumps(quiz),
            json.dumps(answer_key),
        ),
        one=True,
        commit=True,
    )
    quiz_id = quiz_insert.get("id")

    # Insert submission into database
    row = query_db(
        "INSERT INTO submissions (program_id, student_id, code, has_error, feedback) VALUES (%s, %s, %s, %s, %s) RETURNING id",
        (
            data["program_id"],
            data["user_id"],
            data["code"],
            not code_correct,
            json.dumps(code_errors),
        ),
        one=True,
        commit=True,
    )
    return jsonify(
        {
            "id": row["id"],
            "results": final_results,
            "quiz": quiz_json,
            "quiz_id": quiz_id,
        }
    )
