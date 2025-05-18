import re
import openai
import uuid
import json
import os
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

load_dotenv()


client = openai.OpenAI(api_key=os.getenv("CHATGPT_API_KEY"))


def summarize_code(code: str, language: str = "Kannada") -> str:
    prompt = f"""
{code} for this code, give me a detailed paragraph explanation without highlighting any keywords and translate to very very simple spoken {language} while maintaining context and meaning. Give a flowchart in {language} with formulas in JSON format specifically, without translating the JSON keys and keeping them as is:
The JSON KEYS MUST REMAIN IN ENGLISH ("explanation", "translation", "algorithm").

{"{"}
  "explanation": "Detailed paragraph explanation of the given code in the user's preferred language without highlighting keywords. It should describe the code logic clearly and simply, maintaining context and meaning.",
  "translation": "Translated version of the explanation in simple {language} (or specified language), keeping context and meaning intact. Words directly transliterated from English to {language} are enclosed in double quotes.",
  "algorithm": "In {language}, explain how the program works in a detailed manner easy to reproduce, but not too verbose. Use simple words and sentences. Explain each step in the algorithm so we are sure to be thorough, while not revealing the entire code. In bullet points, separated by \\\\n.",
{"}"}

Once generated, please change the JSON keys so they are in English (explanation, translation, algorithm) and keep the values in {language}.
Please ensure that the JSON is valid and keys are in English.
"""

    print(prompt)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
    )
    return response.choices[0].message.content.strip()


def debug_code(code: str, language: str = "Kannada") -> str:
    prompt = f"""
    {code} debug the code and explain the debugging in simple {language}
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
    )
    return response.choices[0].message.content.strip()


def generate_quiz(code: str, actual_code: str = "", language: str = "Kannada") -> str:
    prompt = f"""
     <START OF ACTUAL CODE>{actual_code}<END OF ACTUAL CODE> The above code is the correct version of the code, provided for reference.
     FIRST, IDENTIFY THE GOALS OF THIS ACTUAL CODE.

    <START OF USER ENTERED CODE>{code}<END OF USER ENTERED CODE> For the above code, identify any errors present in it.
    THEN, IDENTIFY IF THIS CODE ACTUALLY FOLLOWS THE GOALS OF THE ACTUAL CODE.
    IF IT DEVIATES AND DOES NOT HAVE THE EXACT FUNCTIONALITY OF THE ACTUAL CODE, THEN THE ERROR IS A FUNCTIONALITY ERROR. THE CODE IS NOT CORRECT.

    If there are any double quotes that you are using that lie within a JSON string, please escape them and any other relevant characters. 
    Provide the minified, escaped, and validated JSON output as described below.

       If any, clearly state them irrespective of whether they are syntactical or logical. Then generate a 10 multiple choice question quiz focusing 6 of them on the part with error. If no error then generate any 10 interesting MCQs on that topic while limiting time complexity question to 1. Give the answer key separately at the end. 
       For the code to be correct, IT MUST ACHIEVE WHAT THE PROVIDED ACTUAL CODE DOES.
       Print everything in {language} in JSON format, WITH JSON KEYS IN ENGLISH! specifically 
  {{
  "code_errors": [{{

      "error_type": "error type description in {language}",
      "description": "detailed explanation of the error in {language}",
      "incorrect_code": "snippet of wrong code in {language}",
      "correct_code": "corrected code snippet in {language}"
    }}]
  ,
  "code_correct": true | false depending on whether the code matches closely the output of the actual code & free from syntax, logical, semantical errors,
  "quiz": [{{
    
      "question": "Question text in {language}!",
      "options": [
        "A) option one, options in {language}!",
        "B) option two",
        "C) option three",
        "D) option four"
      ],
    }}],
  "answer_key": {{
    "0": "Correct option letter (just A or B or C)",
    "1": "Correct option letter (just A or B or C)"
  }},
  "test_inputs": [
    "stdin input to the user generated code in this format separated by \\\\n",
    "generate 3 of these inputs, all of which must be appropriate and test the code for success"
  ]
  }}

  JSON KEYS MUST BE IN ENGLISH, WHILE VALUES IN {language}!
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


def synthesize_speech_to_unique_mp3(
    text: str, voice="kn-IN-SapnaNeural", output_folder: str = "media"
) -> str:
    """
    Synthesizes speech from the provided text and saves it as a uniquely named MP3 file in the specified folder.

    Args:
        text (str): The text to synthesize.
        output_folder (str): The folder to save the MP3 file in.

    Returns:
        str: The full path of the saved MP3 file.
    """
    # Azure credentials
    speech_key = os.getenv("AZURE_SPEECH_KEY")
    service_region = os.getenv("AZURE_REGION")

    # Create the output directory if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Generate a unique filename using UUID
    unique_filename = f"{uuid.uuid4()}.mp3"
    output_path = os.path.join(output_folder, unique_filename)

    # Configure speech synthesis
    speech_config = speechsdk.SpeechConfig(
        subscription=speech_key, region=service_region
    )
    speech_config.speech_synthesis_voice_name = voice
    speech_config.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
    )

    # Set up audio config to write to file
    audio_config = speechsdk.audio.AudioConfig(filename=output_path)

    # Initialize synthesizer
    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=audio_config
    )

    # Perform synthesis
    result = synthesizer.speak_text_async(text).get()

    # Check for success
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"Speech synthesized and saved to: {output_path}")
        return output_path
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print(f"Speech synthesis canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print(f"Error details: {cancellation_details.error_details}")
        return ""


def generate_test_cases_from_ai(
    code: list[str], prompt: str, n_cases: int = 5, language: str = "English"
):
    """
    Generates test cases from GPT based on provided code and prompt.
    Tries to return a parsed list if possible, or returns raw text.
    """
    code_block = "\n".join(code)

    formatted_prompt = f"""
You are a test case generator. Based on the following C code and description, generate {n_cases} diverse and edge-covering test cases.Give output in JSON format.

C Code:
{code_block}

Problem:
{prompt}
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": formatted_prompt}],
        temperature=0.5,
    )

    output = response.choices[0].message.content.strip()

    # Try to extract JSON-like structure from the response
    try:
        match = re.search(r"\[.*\]", output, re.DOTALL)
        if match:
            json_text = match.group(0)
            parsed = json.loads(json_text)
            return parsed
    except Exception:
        pass

    # If not parseable, return raw text
    return output
