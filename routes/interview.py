from flask import Blueprint, jsonify, request

interview_bp = Blueprint("interview", __name__)


@interview_bp.route("/api/interview", methods=["POST"])
def interview():

    data = request.get_json()

    return jsonify({
        "reply": "API Working",
        "done": False
    })