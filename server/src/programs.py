import json
from flask import Blueprint, request, jsonify
from .db import query_db
from .ai import summarize_code, synthesize_speech_to_unique_mp3

programs_bp = Blueprint("programs", __name__)


@programs_bp.route("/programs", methods=["GET"])
def get_programs():
    return jsonify(query_db("SELECT * FROM programs"))


@programs_bp.route("/programs/<int:id>", methods=["GET"])
def program_detail(id):
    prog = query_db("SELECT * FROM programs WHERE id = %s", (id,), one=True)
    summaries = query_db("SELECT * FROM summaries WHERE program_id = %s", (id,))
    return jsonify({"program": prog, "summaries": summaries})


@programs_bp.route("/programs/classroom/<int:class_id>", methods=["GET"])
def programs_by_class(class_id):
    return jsonify(query_db("SELECT * FROM programs WHERE class_id = %s", (class_id,)))


default_languages = {"en": "English", "ka": "Kannada"}


@programs_bp.route("/programs", methods=["POST"])
def create_program():
    data = request.json
    row = query_db(
        "INSERT INTO programs (title, description, code, class_id) VALUES (%s, %s, %s, %s) RETURNING id",
        (data["title"], data["description"], data["code"], data["class_id"]),
        one=True,
        commit=True,
    )

    id = row["id"]

    # Create a summary for the new program
    summary_json = (
        summarize_code(
            data["code"],
            language="Kannada",
        )
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    print(summary_json)

    if summary_json is None:
        return jsonify({"error": "Failed to generate summary"}), 500

    summary = json.loads(summary_json)
    english_summary = summary["explanation"]
    kannada_summary = summary["translation"]
    english_algorithm = summary["english_algorithm"]
    kannada_algorithm = summary["kannada_algorithm"]
    formulas = summary["formulas"]

    english_audio_path = synthesize_speech_to_unique_mp3(
        english_summary,
        output_folder="media",
    )

    kannada_audio_path = synthesize_speech_to_unique_mp3(
        kannada_summary,
        output_folder="media",
    )

    query_db(
        "INSERT INTO summaries (program_id, summary, audio_link, language, algorithm) VALUES (%s, %s, %s, %s, %s) RETURNING program_id",
        (id, english_summary, english_audio_path, "en", english_algorithm),
        commit=True,
    )

    query_db(
        "INSERT INTO summaries (program_id, summary, audio_link, language, algorithm) VALUES (%s, %s, %s, %s, %s) RETURNING program_id",
        (id, kannada_summary, kannada_audio_path, "ka", kannada_algorithm),
        commit=True,
    )

    return jsonify({"id": id})


@programs_bp.route("/programs/<int:id>", methods=["DELETE"])
def delete_program(id):
    # Optionally, delete related summaries and quizzes if needed
    query_db(
        "DELETE FROM summaries WHERE program_id = %s RETURNING program_id",
        (id,),
        commit=True,
    )
    query_db(
        "DELETE FROM quizzes WHERE program_id = %s RETURNING program_id",
        (id,),
        commit=True,
    )
    query_db("DELETE FROM programs WHERE id = %s RETURNING id", (id,), commit=True)
    return jsonify({"status": "deleted", "id": id})
