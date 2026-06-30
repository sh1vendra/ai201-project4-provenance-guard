import uuid

from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

from logger import log_entry, get_log
from signals import groq_signal, stylometric_signal
from store import save_submission, get_submission, update_submission_status

load_dotenv()

app = Flask(__name__)

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    storage_uri="memory://",
    default_limits=[],
)

DISCLAIMER = "This result is an estimate, not proof. False positives and false negatives are possible."

LABEL_MAP = {
    "likely_human": "Likely Human-Written — our system estimates this content was most likely written by a human. This result is an estimate, not proof.",
    "uncertain":    "Uncertain — Unable to Determine Reliably. Our system could not confidently determine whether this was AI or human written. This result is an estimate, not proof.",
    "likely_ai":    "Likely AI-Generated — our system estimates this content was most likely produced by an AI model. This result is an estimate, not proof.",
}


def map_attribution(confidence: float) -> tuple[str, str]:
    if confidence <= 0.30:
        return "likely_human", LABEL_MAP["likely_human"]
    if confidence <= 0.69:
        return "uncertain", LABEL_MAP["uncertain"]
    return "likely_ai", LABEL_MAP["likely_ai"]


@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "ok"})


@app.route("/submit", methods=["POST"])
@limiter.limit("10 per minute;100 per day")
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
    attribution, label = map_attribution(confidence)

    save_submission({
        "content_id": content_id,
        "text": text,
        "creator_id": creator_id,
        "attribution": attribution,
        "confidence": confidence,
        "status": "classified",
    })

    log_entry({
        "event_type": "submission",
        "content_id": content_id,
        "creator_id": creator_id,
        "attribution": attribution,
        "groq_score": groq_score,
        "stylometric_score": stylometric_score,
        "confidence": confidence,
    })

    return jsonify({
        "content_id": content_id,
        "attribution": attribution,
        "label": label,
        "groq_score": groq_score,
        "stylometric_score": stylometric_score,
        "confidence": confidence,
        "disclaimer": DISCLAIMER,
    })


@app.route("/appeal", methods=["POST"])
def appeal():
    body = request.get_json(force=True, silent=True) or {}
    content_id = body.get("content_id", "").strip()
    creator_reasoning = body.get("creator_reasoning", "").strip()
    supporting_evidence = body.get("supporting_evidence", "").strip()

    if not content_id or not creator_reasoning:
        return jsonify({"error": "content_id and creator_reasoning are required"}), 400

    submission = get_submission(content_id)
    if submission is None:
        return jsonify({"error": "submission not found"}), 404

    update_submission_status(content_id, "under_review")

    log_entry({
        "event_type": "appeal",
        "content_id": content_id,
        "creator_id": submission.get("creator_id"),
        "original_attribution": submission.get("attribution"),
        "original_confidence": submission.get("confidence"),
        "appeal_reasoning": creator_reasoning,
        "supporting_evidence": supporting_evidence or None,
    })

    return jsonify({
        "content_id": content_id,
        "status": "under_review",
    })


@app.route("/log", methods=["GET"])
def log():
    return jsonify({"entries": get_log()})


if __name__ == "__main__":
    app.run(debug=True)
