"""Minimal authenticated API with no trading or remote command execution."""
import hmac
import os
from flask import Flask, jsonify, request

from .assistant import answer_question
from .agent import run_task, get_task


def create_app():
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024
    app.json.ensure_ascii = False

    @app.after_request
    def secure_headers(response):
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = "default-src 'none'"
        return response

    @app.get("/health")
    def health():
        return jsonify(status="ok", version="5", trading="disabled")

    @app.post("/api/chat")
    def chat():
        token = os.getenv("ANGEL_API_TOKEN", "")
        if not token:
            return jsonify(error="Server not configured"), 503
        authorization = request.headers.get("Authorization", "")
        if not hmac.compare_digest(authorization, "Bearer " + token):
            return jsonify(error="Unauthorized"), 401
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict) or not isinstance(payload.get("message"), str):
            return jsonify(error="Expected JSON object with message string"), 400
        message = payload["message"].strip()
        if not message or len(message) > 4000:
            return jsonify(error="Message length must be 1..4000"), 400
        try:
            return jsonify(answer=answer_question(message))
        except RuntimeError:
            app.logger.exception("Assistant request failed")
            return jsonify(error="Assistant unavailable"), 503

    @app.post("/api/tasks")
    def tasks():
        token = os.getenv("ANGEL_API_TOKEN", "")
        if not token:
            return jsonify(error="Server not configured"), 503
        if not hmac.compare_digest(request.headers.get("Authorization", ""), "Bearer " + token):
            return jsonify(error="Unauthorized"), 401
        payload = request.get_json(silent=True)
        goal = payload.get("goal") if isinstance(payload, dict) else None
        if not isinstance(goal, str) or not 1 <= len(goal.strip()) <= 4000:
            return jsonify(error="Goal length must be 1..4000"), 400
        if not os.getenv("OPENAI_API_KEY"):
            return jsonify(error="Assistant not configured"), 503
        try:
            return jsonify(run_task(goal.strip()))
        except Exception:
            app.logger.exception("Task execution failed")
            return jsonify(error="Task execution unavailable"), 503

    @app.get("/api/tasks/<task_id>")
    def task_status(task_id):
        token = os.getenv("ANGEL_API_TOKEN", "")
        if not token:
            return jsonify(error="Server not configured"), 503
        if not hmac.compare_digest(request.headers.get("Authorization", ""), "Bearer " + token):
            return jsonify(error="Unauthorized"), 401
        if len(task_id) > 64:
            return jsonify(error="Not found"), 404
        result = get_task(task_id)
        return (jsonify(result), 200) if result else (jsonify(error="Not found"), 404)

    return app
