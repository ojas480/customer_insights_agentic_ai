import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def test_model(model_name):
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "hi"}],
        )
        print(f"SUCCESS with {model_name}!")
    except Exception as e:
        print(f"FAILED {model_name}:", e)

test_model("gemini-1.5-flash")
test_model("gemini-1.5-flash-latest")
test_model("gemini-1.5-pro")
test_model("gemini-pro")
