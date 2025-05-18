import os
import uuid
import openai
import azure.cognitiveservices.speech as speechsdk  # type: ignore
from dotenv import load_dotenv

load_dotenv()

client = openai.OpenAI(api_key=os.getenv("CHATGPT_API_KEY"))

languages = {
    "en": "English",
    "ka": "Kannada",
    "fr": "French",
    "de": "German",
}

voices = {
    "en": "en-IN-NeerjaNeural",
    "ka": "kn-IN-SapnaNeural",
    "fr": "fr-FR-RemyMultilingualNeural",
    "de": "de-DE-SeraphinaMultilingualNeural",
}


def chatbot_speech_helper(
    audio_file_path: str = None,
    text: str = None,
    language: str = "ka",
    previous_messages: list = None,
    actual_program: str = "",
    user_program: str = "",
) -> dict:
    """
    Handles both audio and text input, uses previous messages for context, and returns both text and audio reply.
    """
    # Azure credentials
    speech_key = os.getenv("AZURE_SPEECH_KEY")
    service_region = os.getenv("AZURE_REGION")

    # Step 1: Get user_text from audio or direct text
    user_text = ""
    if audio_file_path:
        speech_config = speechsdk.SpeechConfig(
            subscription=speech_key, region=service_region
        )
        audio_config = speechsdk.audio.AudioConfig(filename=audio_file_path)
        recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config, audio_config=audio_config
        )
        result = recognizer.recognize_once()
        if result.reason != speechsdk.ResultReason.RecognizedSpeech:
            return {"error": f"Speech recognition failed: {result.reason}"}
        user_text = result.text.strip()
    elif text:
        user_text = text.strip()
    else:
        return {"error": "No input provided"}

    # Step 2: Build GPT prompt/messages with context
    messages = []
    if previous_messages:
        for msg in previous_messages:
            role = "assistant" if msg["from"] == "bot" else "user"
            messages.append({"role": role, "content": msg["content"]})
    # Add the current user message
    messages.append({"role": "user", "content": user_text})

    print("Language:", languages[language])

    # System prompt
    system_prompt = (
        f"{actual_program} Above is the actual program. \n"
        # f"{user_program} Above is the program written by the user\n"
        f"You are a helpful coding assistant. Do NOT give full solutions or entire code. "
        f"Instead, reply with a short, helpful *hint, **syntax help, or **concept explanation* in simple and spoken {language}.\n"
        f"Your response should:\n"
        f"- NOT reveal complete code\n"
        f"- Be gentle and encouraging\n"
        f"- Be only 2–3 sentences\n"
        f"- Be in very simple, conversational {languages[language]}\n"
        f"Reply only with the helpful response in {languages[language]}."
    )
    messages = [{"role": "system", "content": system_prompt}] + messages

    # Step 3: GPT-based hint generation
    response = client.chat.completions.create(
        model="gpt-3.5-turbo", messages=messages, temperature=0.6
    )
    bot_reply = response.choices[0].message.content.strip()

    # Step 4: Text-to-speech
    os.makedirs("media", exist_ok=True)
    output_path = f"media/{uuid.uuid4()}.mp3"

    speech_config = speechsdk.SpeechConfig(
        subscription=speech_key, region=service_region
    )
    speech_config.speech_synthesis_voice_name = (
        voices[language] if language in voices else "en-IN-NeerjaNeural"
    )
    speech_config.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
    )
    audio_output_config = speechsdk.audio.AudioConfig(filename=output_path)
    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=audio_output_config
    )
    result = synthesizer.speak_text_async(bot_reply).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"Speech synthesized and saved to: {output_path}")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print(f"Speech synthesis canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print(f"Error details: {cancellation_details.error_details}")
        return ""

    return {
        "user_text": user_text,
        "bot_reply": bot_reply,
        "audio_reply_path": output_path,
    }
