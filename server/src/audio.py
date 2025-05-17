from flask import Blueprint, send_from_directory, abort
import os

audio_bp = Blueprint("audio", __name__)

MEDIA_DIR = os.path.join(os.getcwd(), "media")


@audio_bp.route("/audio/media/<path:filename>", methods=["GET"])
def serve_mp3(filename):
    # Only allow .mp3 files, prevent directory traversal
    if not filename.endswith(".mp3") or ".." in filename or filename.startswith("/"):
        abort(404)
    file_path = os.path.join(MEDIA_DIR, filename)
    print(file_path)
    if not os.path.isfile(file_path):
        abort(404)
    return send_from_directory(MEDIA_DIR, filename, mimetype="audio/mpeg")
