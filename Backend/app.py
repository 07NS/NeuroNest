import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from dotenv import load_dotenv
import traceback
import json


load_dotenv()  # load .env into environment

# -------------------------------
# App setup
# -------------------------------
app = Flask(__name__)
CORS(app)

# -------------------------------
# Gemini Client (NEW SDK)
# -------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_VERSION = os.getenv("GEMINI_API_VERSION", "v1")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "models/gemini-2.5-pro")
print("Using GEMINI_MODEL:", GEMINI_MODEL)
if "embedding" in GEMINI_MODEL:
    print("WARNING: GEMINI_MODEL is an embedding model and won't support generate_content.")


if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY is not set. AI requests will fail. Add it to a local .env or environment variables.")
print("Using GEMINI_MODEL:", GEMINI_MODEL)

client = genai.Client(
    api_key=GEMINI_API_KEY,
    http_options={"api_version": GEMINI_API_VERSION}
)


# -------------------------------
# AI System Prompt
# -------------------------------
LEISURE_AI_PROMPT = """
You are NeuroNest AI — a calm, empathetic, and supportive assistant.

Rules you MUST follow:
- Do NOT provide medical diagnosis
- Do NOT label or classify users
- Speak gently and reassuringly
- Keep responses simple and short
- Focus on awareness, emotional support, and guidance
- Encourage professional consultation gently if appropriate

Tone:
Warm, calm, non-judgmental, hopeful.
"""

# =====================================================
# SCREENING ANALYSIS ROUTE
# =====================================================
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json

    if not data:
        return jsonify({
            "score": 0,
            "riskLevel": "Unavailable",
            "summary": "No screening data received.",
            "recommendations": []
        }), 400

    try:
        # Simple scoring logic (example – you can refine later)
        score = sum(data.values())

        if score <= 6:
            risk = "Low"
            summary = "Your responses suggest low observable risk. Continue monitoring and supporting healthy development."
        elif score <= 12:
            risk = "Moderate"
            summary = "Some responses may indicate developmental differences. Consider observing patterns and seeking guidance."
        else:
            risk = "High"
            summary = "Several responses suggest potential developmental concerns. A professional consultation is recommended."

        return jsonify({
            "score": score,
            "riskLevel": risk,
            "summary": summary,
            "recommendations": [
                "Observe behavioral patterns over time",
                "Engage in supportive communication",
                "Consult a qualified professional if concerns persist"
            ]
        })

    except Exception as e:
        print("ANALYZE ERROR:", e)
        return jsonify({
            "score": 0,
            "riskLevel": "Error",
            "summary": "Something went wrong while analyzing the screening.",
            "recommendations": []
        }), 500


@app.route("/models", methods=["GET"])
def list_models():
    try:
        models = client.models.list()
        names = []
        if isinstance(models, dict):
            for m in models.get("models", []):
                names.append(m.get("name"))
        else:
            for m in models:  # SDK often returns iterable of model objects
                names.append(getattr(m, "name", None) or (m.get("name") if isinstance(m, dict) else None))
        return jsonify({"models": [n for n in names if n]})
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# =====================================================
# AI CHATBOT ROUTE
# =====================================================
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json or {}
        user_message = (data.get("message") or "").strip()
        print("CHAT REQUEST:", data)

        if not user_message:
            return jsonify({"reply": "I'm here whenever you're ready 🌱"})

        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=f"{LEISURE_AI_PROMPT}\n\nUser: {user_message}\nAssistant:"
            )
        except Exception as e:
            print("SDK ERROR during generate_content:")
            traceback.print_exc()
            return jsonify({"reply": "I'm here with you, but something went wrong. Please try again 💙"}), 500

        print("RAW MODEL RESPONSE:", repr(response))

        # Robust extraction
        text = None
        if isinstance(response, dict):
            text = response.get("text") or (response.get("candidates") and response["candidates"][0].get("content"))
        else:
            text = getattr(response, "text", None)
            if not text and getattr(response, "candidates", None):
                cand = response.candidates[0]
                text = getattr(cand, "content", None) or getattr(cand, "text", None)

        if not text:
            print("UNEXPECTED MODEL RESPONSE SHAPE:", response)
            return jsonify({"reply": "Received unexpected response from model. Check server logs."}), 500
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=f"{LEISURE_AI_PROMPT}\n\nUser: {user_message}\nAssistant:"
        )

        print("CHAT RESPONSE:", text)
        return jsonify({"reply": text})

    except Exception as e:
        print("CHAT ERROR:", e)
        traceback.print_exc()
        return jsonify({"reply": "I'm here with you, but something went wrong. Please try again 💙"}), 500


# =====================================================
# HEALTH CHECK (OPTIONAL BUT GOOD)
# =====================================================
# Quick health endpoint for debugging
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "ok": True,
        "gemini_key_loaded": bool(GEMINI_API_KEY),
        "gemini_api_version": GEMINI_API_VERSION
    })


@app.route("/", methods=["GET"])
def home():
    return "NeuroNest backend is running."

# -------------------------------
# Run locally (Render ignores this)
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)

