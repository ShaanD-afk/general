import time
import requests
import os
import base64
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("JUDGE_URL")
SUBMISSION_URL = f"{BASE_URL}/submissions"
GET_SUBMISSION_URL = lambda token: f"{BASE_URL}/submissions/{token}?base64_encoded=true"


print(BASE_URL)


def judge(code, input=None, language=50):
    data = {
        "source_code": code,
        "language_id": language,
        "stdin": input,
    }

    response = requests.post(SUBMISSION_URL, json=data)

    if response.status_code < 300:
        token = response.json().get("token")
    else:
        print("Error submitting!:", response.text)
        return None

    # Wait for the submission to be processed
    time.sleep(3)

    submission_response = requests.get(GET_SUBMISSION_URL(token))
    if not submission_response.ok:
        return False, "Submission fetch failed", {}

    submission_data = submission_response.json()

    # Decode base64 stdout if present
    stdout_b64 = submission_data.get("stdout")
    stdout = None
    if stdout_b64:
        try:
            stdout = base64.b64decode(stdout_b64).decode("utf-8")
        except Exception as e:
            stdout = ""
    else:
        stdout = ""

    # Decode base64 compile_output if present
    compile_output_b64 = submission_data.get("compile_output")
    compile_output = None
    if compile_output_b64:
        try:
            compile_output = base64.b64decode(compile_output_b64).decode("utf-8")
        except Exception as e:
            compile_output = ""
    else:
        compile_output = ""

    return {
        "stdout": stdout,
        "compile_output": compile_output,
        "compile_error": len(compile_output) > 0,
    }
