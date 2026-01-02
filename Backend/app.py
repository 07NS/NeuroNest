from flask import Flask, request, jsonify
from flask_cors import CORS
from ai_logic import analyze_screening

app = Flask(__name__)
CORS(app)

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    result = analyze_screening(data)
    return jsonify(result)

if __name__ == "__main__":
    app.run(port=3000, debug=True)

@app.route("/")
def home():
    return {
        "status": "NeuroNest backend is running",
        "message": "Use /analyze endpoint for screening"
    }
