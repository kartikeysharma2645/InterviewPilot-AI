from flask import Blueprint, jsonify, request

from models.session_manager import SessionManager
from services.curriculum_repository import CurriculumRepository
from services.gemini_service import GeminiService
from services.interview_engine import InterviewEngine


interview_bp = Blueprint("interview", __name__)


# Shared service instances for the Flask application.
session_manager = SessionManager()
curriculum_repository = CurriculumRepository()
gemini_service = GeminiService()

engine = InterviewEngine(
    session_manager=session_manager,
    curriculum_repository=curriculum_repository,
    gemini_service=gemini_service,
)


@interview_bp.route("/api/interview", methods=["POST"])
def interview():
    """
    Start or continue an interview.

    Start:
    {
        "sessionId": "demo-001",
        "candidate": "CAND-001"
    }

    Continue:
    {
        "sessionId": "demo-001",
        "message": "Candidate's answer"
    }
    """

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Request body must be valid JSON."
        }), 400

    session_id = data.get("sessionId")

    if not session_id:
        return jsonify({
            "error": "sessionId is required."
        }), 400

    try:
        # ---------------------------------------------------------
        # START INTERVIEW
        # ---------------------------------------------------------
        if "candidate" in data:
            candidate_id = data.get("candidate")

            if not candidate_id:
                return jsonify({
                    "error": "candidate is required when starting an interview."
                }), 400

            result = engine.start_interview(
                session_id=session_id,
                candidate_id=candidate_id,
            )

            return jsonify(result), 200

        # ---------------------------------------------------------
        # CONTINUE INTERVIEW
        # ---------------------------------------------------------
        if "message" in data:
            message = data.get("message")

            if not message:
                return jsonify({
                    "error": "message is required when continuing an interview."
                }), 400

            result = engine.continue_interview(
                session_id=session_id,
                message=message,
            )

            return jsonify(result), 200

        # ---------------------------------------------------------
        # INVALID REQUEST
        # ---------------------------------------------------------
        return jsonify({
            "error": "Request must contain either 'candidate' or 'message'."
        }), 400

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except RuntimeError as error:
        print(f"Interview runtime error: {error}")

        return jsonify({
            "error": str(error)
        }), 500

    except Exception as error:
        print(f"Unexpected interview API error: {error}")

        return jsonify({
            "error": "Internal server error."
        }), 500