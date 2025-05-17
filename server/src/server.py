import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from .auth import auth_bp
from .classrooms import classrooms_bp
from .programs import programs_bp
from .quiz import quiz_bp
from .submissions import submissions_bp
from .summaries import summaries_bp
from .users import users_bp
from .audio import audio_bp
from .chat import chat_bp

load_dotenv()

app = Flask(__name__)

CORS(
    app,
    supports_credentials=True,
    origins=os.getenv("CORS_ALLOWED_ORIGINS", "*").split(","),
)

app.secret_key = os.getenv("SECRET_KEY")


@app.route("/")
def home():
    return "Flask server is running!"


app.register_blueprint(auth_bp)
app.register_blueprint(classrooms_bp)
app.register_blueprint(programs_bp)
app.register_blueprint(quiz_bp)
app.register_blueprint(submissions_bp)
app.register_blueprint(summaries_bp)
app.register_blueprint(users_bp)
app.register_blueprint(audio_bp)
app.register_blueprint(chat_bp)


def main():
    app.run(debug=True, port=5051, host="0.0.0.0", threaded=True)
