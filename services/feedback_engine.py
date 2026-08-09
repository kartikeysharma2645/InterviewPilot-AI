import json
from typing import Any

from services.gemini_service import GeminiService


class FeedbackEngine:
    """Generates structured final interview feedback."""

    def __init__(self, gemini_service: GeminiService):
        self.gemini = gemini_service

    def generate_feedback(
        self,
        session,
    ) -> dict[str, Any]:
        """Generate final feedback from all interview evaluations."""

        evaluations = session.evaluations

        if not evaluations:
            raise ValueError(
                "Cannot generate feedback without evaluations."
            )

        evaluation_text = json.dumps(
            evaluations,
            indent=2,
            ensure_ascii=False,
        )

        prompt = f"""
You are generating the final report for a technical interview.

Candidate:
- Role: {session.candidate_profile.job_role}
- Experience: {session.candidate_profile.years_experience} years
- Education: {session.candidate_profile.education}

The candidate was evaluated across multiple technical
curriculum topics.

Interview evaluations:
{evaluation_text}

Generate a concise and useful final interview report.

Return ONLY valid JSON.
Do not use Markdown.
Do not include ```json.
Do not include any text outside the JSON object.

Use exactly this schema:

{{
  "summary": "",
  "strengths": [],
  "gaps": [],
  "next": ""
}}

Rules:
- summary should be a concise overall assessment.
- strengths should contain 2 to 4 specific strengths supported
  by the interview.
- gaps should contain 2 to 4 specific technical areas that
  need improvement.
- next should provide a concise recommendation for what the
  candidate should focus on next.
- Do not invent skills that were not demonstrated.
- Base the report only on the interview evaluations.
"""

        response = self.gemini.generate(prompt)

        try:
            feedback = json.loads(response)

        except json.JSONDecodeError as error:
            raise RuntimeError(
                "Gemini returned invalid feedback JSON: "
                f"{response}"
            ) from error

        required_fields = {
            "summary",
            "strengths",
            "gaps",
            "next",
        }

        missing_fields = (
            required_fields - feedback.keys()
        )

        if missing_fields:
            raise RuntimeError(
                "Feedback missing fields: "
                f"{missing_fields}"
            )

        if not isinstance(feedback["summary"], str):
            raise RuntimeError(
                "Feedback summary must be a string."
            )

        if not isinstance(feedback["strengths"], list):
            raise RuntimeError(
                "Feedback strengths must be a list."
            )

        if not isinstance(feedback["gaps"], list):
            raise RuntimeError(
                "Feedback gaps must be a list."
            )

        if not isinstance(feedback["next"], str):
            raise RuntimeError(
                "Feedback next must be a string."
            )

        return feedback