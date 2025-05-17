from flask import Blueprint, request, jsonify
from .db import query_db

summaries_bp = Blueprint("summaries", __name__)


@summaries_bp.route("/summaries/program/<int:pid>", methods=["GET"])
def summaries_by_program(pid):
    return jsonify(query_db("SELECT * FROM summaries WHERE program_id = %s", (pid,)))


@summaries_bp.route("/summaries/program/<int:pid>/lang/<lang>", methods=["GET"])
def summary_lang(pid, lang):
    return jsonify(
        query_db(
            "SELECT * FROM summaries WHERE program_id = %s AND language = %s",
            (pid, lang),
            one=True,
        )
    )


@summaries_bp.route("/summaries", methods=["POST"])
def create_summary():
    data = request.json
    row = query_db(
        "INSERT INTO summaries (program_id, language, summary, test_cases, audio_link) VALUES (%s, %s, %s, %s, %s) RETURNING id",
        (
            data["program_id"],
            data["language"],
            data["summary"],
            data["test_cases"],
            data["audio_link"],
        ),
        one=True,
        commit=True,
    )
    return jsonify({"id": row["id"]})
