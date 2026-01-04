import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai

# -------------------------------
# App setup
# -------------------------------
app = Flask(__name__)
CORS(app)

# -------------------------------
# Gemini Client (NEW SDK)
# -------------------------------
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
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

# =====================================================
# AI CHATBOT ROUTE
# =====================================================
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({
                "reply": "I'm here whenever you're ready 🌱"
            })

        response = client.models.generate_content(
            model="models/gemini-1.5-flash-latest",
            contents=f"{LEISURE_AI_PROMPT}\n\nUser: {user_message}\nAssistant:"
        )

        return jsonify({
            "reply": response.text
        })

    except Exception as e:
        print("CHAT ERROR:", e)
        return jsonify({
            "reply": "I'm here with you, but something went wrong. Please try again 💙"
        }), 500

# =====================================================
# HEALTH CHECK (OPTIONAL BUT GOOD)
# =====================================================
@app.route("/", methods=["GET"])
def home():
    return "NeuroNest backend is running."

# -------------------------------
# Run locally (Render ignores this)
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)

