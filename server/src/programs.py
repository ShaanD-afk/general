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


def generate_and_save_summaries(program_id: int, code: str):
    """
    Generates summaries and audio for all supported languages and saves them to the DB.
    Removes old summaries first.
    """

    languages = [
        {
            "key": "en",
            "language": "English",
            "summary_field": "explanation",
            "algorithm_field": "english_algorithm",
            "voice": "en-IN-NeerjaNeural",
        },
        {
            "key": "ka",
            "language": "Kannada",
            "summary_field": "translation",
            "algorithm_field": "kannada_algorithm",
            "voice": "kn-IN-SapnaNeural",
        },
        {
            "key": "fr",
            "language": "French",
            "summary_field": "french_translation",
            "algorithm_field": "french_algorithm",
            "voice": "fr-FR-RemyMultilingualNeural",
        },
        {
            "key": "de",
            "language": "German",
            "summary_field": "german_translation",
            "algorithm_field": "german_algorithm",
            "voice": "de-DE-SeraphinaMultilingualNeural",
        },
    ]

    # Remove old summaries
    query_db(
        "DELETE FROM summaries WHERE program_id = %s RETURNING program_id",
        (program_id,),
        commit=True,
    )

    for language in languages:
        # Generate summaries and audio for each language
        summary_json = (
            summarize_code(code, language=language["language"])
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        if summary_json is None:
            raise Exception("Failed to generate summary")

        print(summary_json)

        summary = json.loads(summary_json)
        summary_text = summary["translation"]
        algorithm_text = summary["algorithm"]

        audio_path = synthesize_speech_to_unique_mp3(
            summary_text,
            output_folder="media",
            voice=language["voice"],
        )

        # Save the summary and audio to the database
        query_db(
            "INSERT INTO summaries (program_id, summary, audio_link, language, algorithm) VALUES (%s, %s, %s, %s, %s) RETURNING program_id",
            (program_id, summary_text, audio_path, language["key"], algorithm_text),
            commit=True,
        )

    # # Generate new summaries
    # summary_json = (
    #     summarize_code(code).replace("```json", "").replace("```", "").strip()
    # )

    # if summary_json is None:
    #     raise Exception("Failed to generate summary")

    # print(summary_json)

    # summary = json.loads(summary_json)
    # english_summary = summary["explanation"]
    # kannada_summary = summary["translation"]
    # french_summary = summary["french_translation"]
    # german_summary = summary["german_translation"]
    # english_algorithm = summary["english_algorithm"]
    # kannada_algorithm = summary["kannada_algorithm"]
    # french_algorithm = summary["french_algorithm"]
    # german_algorithm = summary["german_algorithm"]

    # english_audio_path = synthesize_speech_to_unique_mp3(
    #     english_summary,
    #     output_folder="media",
    # )

    # kannada_audio_path = synthesize_speech_to_unique_mp3(
    #     kannada_summary,
    #     output_folder="media",
    # )

    # french_audio_path = synthesize_speech_to_unique_mp3(
    #     french_summary, output_folder="media", voice="fr-FR-RemyMultilingualNeural"
    # )

    # german_audio_path = synthesize_speech_to_unique_mp3(
    #     german_summary, output_folder="media", voice="de-DE-SeraphinaMultilingualNeural"
    # )

    # # Save all summaries
    # query_db(
    #     "INSERT INTO summaries (program_id, summary, audio_link, language, algorithm) VALUES (%s, %s, %s, %s, %s)",
    #     (program_id, english_summary, english_audio_path, "en", english_algorithm),
    #     commit=True,
    # )
    # query_db(
    #     "INSERT INTO summaries (program_id, summary, audio_link, language, algorithm) VALUES (%s, %s, %s, %s, %s)",
    #     (program_id, kannada_summary, kannada_audio_path, "ka", kannada_algorithm),
    #     commit=True,
    # )
    # query_db(
    #     "INSERT INTO summaries (program_id, summary, audio_link, language, algorithm) VALUES (%s, %s, %s, %s, %s)",
    #     (program_id, french_summary, french_audio_path, "fr", french_algorithm),
    #     commit=True,
    # )
    # query_db(
    #     "INSERT INTO summaries (program_id, summary, audio_link, language, algorithm) VALUES (%s, %s, %s, %s, %s)",
    #     (program_id, german_summary, german_audio_path, "de", german_algorithm),
    #     commit=True,
    # )


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

    try:
        generate_and_save_summaries(id, data["code"])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"id": id})


@programs_bp.route("/programs/<int:id>/regenerate_summaries", methods=["POST"])
def regenerate_summaries(id):
    # Get the program code
    prog = query_db("SELECT code FROM programs WHERE id = %s", (id,), one=True)
    if not prog:
        return jsonify({"error": "Program not found"}), 404

    try:
        generate_and_save_summaries(id, prog["code"])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"status": "summaries regenerated", "program_id": id})


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
