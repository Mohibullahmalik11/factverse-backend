import os
import json
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = Flask(__name__)
CORS(app)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-3.8-flash"


def ask_ai(prompt):
    for attempt in range(3):
        try:
            response = client.models.generate_content(model=MODEL, contents=prompt)
            return response.text
        except Exception as e:
            if "503" in str(e) and attempt < 2:
                time.sleep(3)
                continue
            raise


@app.route("/")
def home():
    return "Backend chal raha hai!"


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "Sawal khali hai"}), 400
    if len(question) > 500:
        return jsonify({"error": "Sawal bohat lamba hai (500 characters tak)"}), 400

    prompt = f"""You are a friendly knowledge assistant on a facts website.
Answer the question clearly in a short, simple way (under 150 words).
Reply in the same language the user wrote in.
If you are not sure about something, say so honestly instead of guessing.

Question: {question}"""

    try:
        return jsonify({"answer": ask_ai(prompt)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.get_json()
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"error": "Text khali hai"}), 400

    prompt = f"Neeche diye gaye notes ka asaan zabaan mein summary bullet points mein likho:\n\n{text}"

    try:
        return jsonify({"summary": ask_ai(prompt)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/quiz", methods=["POST"])
def quiz():
    data = request.get_json()
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"error": "Text khali hai"}), 400

    prompt = f"""Neeche diye gaye notes se exactly 5 multiple choice questions banao.
Sirf valid JSON return karo, aur kuch nahi (na markdown).
Format:
[
  {{"question": "...", "options": ["A", "B", "C", "D"], "answer": 0}}
]
"answer" sahi option ka index hai (0 se 3 tak).

Notes:
{text}"""

    try:
        raw = ask_ai(prompt).strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        questions = json.loads(raw)
        return jsonify({"questions": questions})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)