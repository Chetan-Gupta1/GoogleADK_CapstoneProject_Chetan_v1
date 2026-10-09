import os
from pathlib import Path

from google import genai
from google.genai import types
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent


def generate_text(prompt, response_schema=None):
    load_dotenv(BASE_DIR / ".env")
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Set GOOGLE_API_KEY in the project .env file for AI generation.")
    config = types.GenerateContentConfig(temperature=0.2)
    if response_schema is not None:
        config.response_mime_type = "application/json"
        config.response_json_schema = response_schema.model_json_schema()
    with genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=120000)) as client:
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash"),
            contents=prompt,
            config=config,
        )
    if not response.text:
        raise RuntimeError("Gemini returned no text. Check safety feedback and model access.")
    return response.text

def generate_slide_title(story):
    prompt = f"""
    You are an executive strategy consultant.
    Create a concise executive slide title.
    Business Story:
    {story}
    Rules:
    - maximum 10 words
    - insight-led
    - executive tone
    """
    return generate_text(prompt)


def generate_slide_bullets(story):

    prompt = f"""
    Create 4 executive presentation bullets.
    Business Story:
    {story}
    Rules:
    - 4 bullets only
    - maximum 18 words each
    - insight focused
    """
    return generate_text(prompt)