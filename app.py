import uuid

from flask import Flask, jsonify, request
from dotenv import load_dotenv

from logger import log_entry, get_log
from signals import groq_signal, stylometric_signal

load_dotenv()

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "ok"})


@app.route("/submit", methods=["POST"])
def submit():
    body = request.get_json(force=True, silent=True) or {}
    text = body.get("text", "")
    creator_id = body.get("creator_id", "")

    content_id = str(uuid.uuid4())

    groq_result = groq_signal(text)
    groq_score = groq_result["ai_likelihood"]

    stylo_result = stylometric_signal(text)
    stylometric_score = stylo_result["score"]

    confidence = round(0.6 * groq_score + 0.4 * stylometric_score, 4)

    log_entry({
        "content_id": content_id,
        "creator_id": creator_id,
        "attribution": "pending",
        "groq_score": groq_score,
        "stylometric_score": stylometric_score,
        "confidence": confidence,
    })

    return jsonify({
        "content_id": content_id,
        "attribution": "pending",
        "groq_score": groq_score,
        "stylometric_score": stylometric_score,
        "confidence": confidence,
        "label": "Uncertain — Unable to Determine Reliably",
    })


@app.route("/log", methods=["GET"])
def log():
    return jsonify({"entries": get_log()})


if __name__ == "__main__":
    app.run(debug=True)
