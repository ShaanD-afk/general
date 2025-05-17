import os
import uuid
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from .db import query_db
from .chatbot.voice import chatbot_speech_helper

from pydub import AudioSegment
import base64

chat_bp = Blueprint("chat", __name__)
os.makedirs("temp", exist_ok=True)


def save_as_wav(uploaded_file, out_path):
    temp_path = out_path + ".tmp"
    uploaded_file.save(temp_path)
    try:
        audio = AudioSegment.from_file(temp_path)
        audio.export(out_path, format="wav")
        os.remove(temp_path)
        return out_path
    except Exception as e:
        os.remove(temp_path)
        raise RuntimeError(f"Audio conversion failed: {e}")


def get_previous_messages(program_id, user_id, limit=10):
    messages = query_db(
        """
        SELECT content, "from", sent_at FROM messages
        WHERE program_id = %s AND user_id = %s
        ORDER BY sent_at DESC LIMIT %s
        """,
        (program_id, user_id, limit),
    )
    return list(reversed(messages))


def get_actual_program(program_id):
    prog = query_db("SELECT * FROM programs WHERE id = %s", (program_id,), one=True)
    if not prog:
        return ""
    return prog.get("code", "")


@chat_bp.route("/chat/message", methods=["POST"])
def chat_message():
    """
    Accepts a message as text or audio.
    Saves it to the messages table for later processing.
    Expects: user_id, program_id, and either text or audio (multipart/form-data or JSON).
    Returns: bot reply in text and audio.
    """
    try:
        # Prefer form fields if present
        if request.form:
            user_id = request.form.get("user_id")
            program_id = request.form.get("program_id")
            language = request.form.get("language") or "en"
            if not user_id or not program_id:
                return jsonify({"error": "user_id and program_id required"}), 400
            prev_messages = get_previous_messages(program_id, user_id)
            actual_program = get_actual_program(program_id)

            if "text" in request.form:
                user_text = request.form["text"]
                query_db(
                    'INSERT INTO messages (program_id, user_id, content, "from") VALUES (%s, %s, %s, %s) RETURNING program_id',
                    (program_id, user_id, user_text, "student"),
                    commit=True,
                )
                bot_result = chatbot_speech_helper(
                    text=user_text,
                    language=language,
                    previous_messages=prev_messages,
                    actual_program=actual_program,
                )
                if "error" in bot_result:
                    return jsonify({"error": bot_result["error"]}), 400
                # Save bot reply and audio link
                query_db(
                    'INSERT INTO messages (program_id, user_id, content, "from", audio_link) VALUES (%s, %s, %s, %s, %s) RETURNING program_id',
                    (
                        program_id,
                        user_id,
                        bot_result["bot_reply"],
                        "bot",
                        bot_result.get("audio_reply_path"),
                    ),
                    commit=True,
                )
                return jsonify(bot_result)

            if "audio" in request.files:
                audio_file = request.files["audio"]
                filename = f"{uuid.uuid4()}.wav"
                filepath = os.path.join("temp", secure_filename(filename))
                try:
                    save_as_wav(audio_file, filepath)
                except Exception as e:
                    return jsonify({"error": str(e)}), 400

                # Save student audio as content, no audio_link
                query_db(
                    'INSERT INTO messages (program_id, user_id, content, "from") VALUES (%s, %s, %s, %s) RETURNING program_id',
                    (program_id, user_id, filepath, "student"),
                    commit=True,
                )

                bot_result = chatbot_speech_helper(
                    audio_file_path=filepath,
                    language=language,
                    previous_messages=prev_messages,
                    actual_program=actual_program,
                )
                if "error" in bot_result:
                    return jsonify({"error": bot_result["error"]}), 400
                # Save bot reply and audio link
                query_db(
                    'INSERT INTO messages (program_id, user_id, content, "from", audio_link) VALUES (%s, %s, %s, %s, %s) RETURNING program_id',
                    (
                        program_id,
                        user_id,
                        bot_result["bot_reply"],
                        "bot",
                        bot_result.get("audio_reply_path"),
                    ),
                    commit=True,
                )
                return jsonify(bot_result)

            return jsonify({"error": "No valid input provided"}), 400

        # If JSON, handle as before
        if request.is_json:
            data = request.get_json()
            user_id = data.get("user_id")
            program_id = data.get("program_id")
            language = data.get("language", "en")
            if not user_id or not program_id:
                return jsonify({"error": "user_id and program_id required"}), 400
            prev_messages = get_previous_messages(program_id, user_id)
            actual_program = get_actual_program(program_id)

            if "text" in data:
                user_text = data["text"]
                query_db(
                    'INSERT INTO messages (program_id, user_id, content, "from") VALUES (%s, %s, %s, %s) RETURNING program_id',
                    (program_id, user_id, user_text, "student"),
                    commit=True,
                )
                bot_result = chatbot_speech_helper(
                    text=user_text,
                    language=language,
                    previous_messages=prev_messages,
                    actual_program=actual_program,
                )
                if "error" in bot_result:
                    return jsonify({"error": bot_result["error"]}), 400
                # Save bot reply and audio link
                query_db(
                    'INSERT INTO messages (program_id, user_id, content, "from", audio_link) VALUES (%s, %s, %s, %s, %s) RETURNING program_id',
                    (
                        program_id,
                        user_id,
                        bot_result["bot_reply"],
                        "bot",
                        bot_result.get("audio_reply_path"),
                    ),
                    commit=True,
                )
                return jsonify(bot_result)

            if "audio_base64" in data:
                try:
                    audio_bytes = base64.b64decode(data["audio_base64"])
                    filename = f"{uuid.uuid4()}.wav"
                    filepath = os.path.join("temp", filename)
                    with open(filepath, "wb") as f:
                        f.write(audio_bytes)
                except Exception as e:
                    return jsonify({"error": f"Audio decode failed: {e}"}), 400

                # Save student audio as content, no audio_link
                query_db(
                    'INSERT INTO messages (program_id, user_id, content, "from") VALUES (%s, %s, %s, %s) RETURNING program_id',
                    (program_id, user_id, filepath, "student"),
                    commit=True,
                )
                bot_result = chatbot_speech_helper(
                    audio_file_path=filepath,
                    language=language,
                    previous_messages=prev_messages,
                    actual_program=actual_program,
                )
                if "error" in bot_result:
                    return jsonify({"error": bot_result["error"]}), 400
                # Save bot reply and audio link
                query_db(
                    'INSERT INTO messages (program_id, user_id, content, "from", audio_link) VALUES (%s, %s, %s, %s, %s) RETURNING program_id',
                    (
                        program_id,
                        user_id,
                        bot_result["bot_reply"],
                        "bot",
                        bot_result.get("audio_reply_path"),
                    ),
                    commit=True,
                )
                return jsonify(bot_result)

            return jsonify({"error": "No valid input provided"}), 400

        return jsonify({"error": "No valid input provided"}), 400

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@chat_bp.route("/chat/messages", methods=["GET"])
def get_messages():
    """
    Fetch all messages for a given user_id and program_id.
    Expects user_id and program_id as query parameters.
    """
    user_id = request.args.get("user_id")
    program_id = request.args.get("program_id")
    if not user_id or not program_id:
        return jsonify({"error": "user_id and program_id required"}), 400
    messages = query_db(
        "SELECT * FROM messages WHERE user_id = %s AND program_id = %s ORDER BY sent_at ASC",
        (user_id, program_id),
    )
    return jsonify(messages)
