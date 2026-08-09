from services.feedback_engine import FeedbackEngine
import json
from typing import Any

from models.session_manager import SessionManager
from services.candidate_analyzer import analyze_candidate
from services.curriculum_repository import CurriculumRepository
from services.gemini_service import GeminiService
from services.interview_planner import InterviewPlanner
from utils.json_loader import get_candidate


class InterviewEngine:
    """Orchestrates the complete interview lifecycle."""

    def __init__(
        self,
        session_manager: SessionManager,
        curriculum_repository: CurriculumRepository,
        gemini_service: GeminiService,
    ):
        self.sessions = session_manager
        self.curriculum = curriculum_repository
        self.gemini = gemini_service

        self.planner = InterviewPlanner(
            self.curriculum
        )

        self.feedback_engine = FeedbackEngine(
            self.gemini
        )

    def start_interview(
        self,
        session_id: str,
        candidate_id: str,
    ) -> dict[str, Any]:
        """Create a session and generate the first interview question."""

        existing_session = self.sessions.get_session(
            session_id
        )

        if existing_session is not None:
            raise ValueError(
                f"Session already exists: {session_id}"
            )

        candidate = get_candidate(candidate_id)

        if candidate is None:
            raise ValueError(
                f"Candidate not found: {candidate_id}"
            )

        profile = analyze_candidate(candidate)

        plan = self.planner.create_plan(profile)

        session = self.sessions.create_session(
            session_id=session_id,
            candidate=candidate,
            candidate_profile=profile,
            interview_plan=plan,
        )

        question = self._generate_primary_question(
            session
        )

        return self._set_question(
            session,
            question,
            question_type="primary",
        )

    def continue_interview(
        self,
        session_id: str,
        message: str,
    ) -> dict[str, Any]:
        """Process a candidate answer and continue the interview."""

        session = self.sessions.get_session(
            session_id
        )

        if session is None:
            raise ValueError(
                f"Session not found: {session_id}"
            )

        if session.completed:
            raise ValueError(
                "Interview is already completed."
            )

        if not message.strip():
            raise ValueError(
                "Interview message cannot be empty."
            )

        self.sessions.add_message(
            session_id,
            "user",
            message,
        )

        evaluation = self._evaluate_answer(
            session,
            message,
        )

        self.sessions.add_evaluation(
            session_id,
            evaluation,
        )

        if self._should_follow_up(
            session,
            evaluation,
        ):
            follow_up = self._generate_follow_up(
                session,
                evaluation,
            )

            session.followups_asked += 1

            return self._set_question(
                session,
                follow_up,
                question_type="follow_up",
            )

        return self._advance_or_finish(session)

    def _generate_primary_question(
        self,
        session,
    ) -> str:
        """Generate the next primary interview question."""

        question_plan = session.interview_plan.questions[
            session.current_question_index
        ]

        prompt = f"""
You are conducting a realistic technical interview.

Candidate profile:
- Role: {session.candidate_profile.job_role}
- Experience: {session.candidate_profile.years_experience} years
- Education: {session.candidate_profile.education}

Curriculum day:
{question_plan.day}

Topic:
{question_plan.title}

Learning objectives:
{chr(10).join("- " + obj for obj in question_plan.objectives)}

Starting difficulty:
{question_plan.difficulty}

Reason for selecting this topic:
{question_plan.reason}

Ask exactly ONE technical interview question.

Requirements:
- The question must test actual understanding.
- Match the candidate's experience level.
- Focus on the curriculum topic and objectives.
- Do not ask multiple questions.
- Do not provide the answer.
- Do not mention the curriculum, mission history, or internal interview process.
- Do not say "Question 1" or similar labels.
"""

        return self.gemini.generate(prompt)

    def _evaluate_answer(
        self,
        session,
        answer: str,
    ) -> dict[str, Any]:
        """Evaluate a candidate answer using structured JSON."""

        prompt = f"""
You are evaluating a technical interview answer.

Candidate:
- Role: {session.candidate_profile.job_role}
- Experience: {session.candidate_profile.years_experience} years

Question:
{session.current_question}

Candidate answer:
{answer}

Evaluate the answer strictly against the question.

Return ONLY valid JSON.
Do not use Markdown.
Do not include ```json.
Do not include any text outside the JSON object.

Use exactly this schema:

{{
  "score": 0,
  "technical_correctness": 0,
  "depth": 0,
  "reasoning_quality": 0,
  "follow_up_needed": false,
  "feedback": ""
}}

Rules:
- score must be an integer from 1 to 10.
- technical_correctness must be an integer from 1 to 10.
- depth must be an integer from 1 to 10.
- reasoning_quality must be an integer from 1 to 10.
- follow_up_needed must be true only when a focused follow-up
  question would meaningfully test the candidate's understanding.
- Set follow_up_needed to false if the candidate clearly lacks
  the prerequisite knowledge and a follow-up would not be useful.
- feedback should briefly explain the evaluation.
"""

        evaluation_text = self.gemini.generate(
            prompt
        )

        try:
            evaluation = json.loads(
                evaluation_text
            )

        except json.JSONDecodeError as error:
            raise RuntimeError(
                "Gemini returned invalid evaluation JSON: "
                f"{evaluation_text}"
            ) from error

        required_fields = {
            "score",
            "technical_correctness",
            "depth",
            "reasoning_quality",
            "follow_up_needed",
            "feedback",
        }

        missing_fields = (
            required_fields - evaluation.keys()
        )

        if missing_fields:
            raise RuntimeError(
                "Evaluation missing fields: "
                f"{missing_fields}"
            )

        if not isinstance(
            evaluation["follow_up_needed"],
            bool,
        ):
            raise RuntimeError(
                "follow_up_needed must be a boolean."
            )

        for field in (
            "score",
            "technical_correctness",
            "depth",
            "reasoning_quality",
        ):
            if not isinstance(
                evaluation[field],
                int,
            ):
                raise RuntimeError(
                    f"{field} must be an integer."
                )

            if not 1 <= evaluation[field] <= 10:
                raise RuntimeError(
                    f"{field} must be between 1 and 10."
                )

        evaluation["question"] = (
            session.current_question
        )

        evaluation["answer"] = answer

        return evaluation

    def _should_follow_up(
        self,
        session,
        evaluation: dict[str, Any],
    ) -> bool:
        """Determine whether the current answer deserves a follow-up."""

        if session.followups_asked >= 1:
            return False

        return evaluation["follow_up_needed"] is True

    def _generate_follow_up(
        self,
        session,
        evaluation: dict[str, Any],
    ) -> str:
        """Generate one focused follow-up question."""

        prompt = f"""
You are conducting a realistic technical interview.

Previous question:
{session.current_question}

Candidate answer:
{session.history[-1]["content"]}

Evaluation:
{evaluation["feedback"]}

Ask exactly ONE concise follow-up question.

The follow-up must:
- Directly relate to the previous question.
- Probe a specific weakness, assumption, or missing detail.
- Be appropriate for the candidate's experience level.
- Test understanding rather than recall.
- Not repeat the previous question.
- Not contain multiple questions.
- Not provide the answer.
"""

        return self.gemini.generate(
            prompt
        )

    def _advance_or_finish(
        self,
        session,
    ) -> dict[str, Any]:
        """Advance to the next primary question or finish."""

        session.primary_questions_asked += 1

        # Interview is complete.
        if (
            session.primary_questions_asked
            >= len(session.interview_plan.questions)
        ):
            feedback = self.feedback_engine.generate_feedback(
                session
            )

            self.sessions.mark_completed(
                session.session_id
            )

            return {
                "reply": "Interview completed.",
                "done": True,
                "feedback": feedback,
            }

        # Move to the next primary question.
        self.sessions.advance_question(
            session.session_id
        )

        session.followups_asked = 0

        question = self._generate_primary_question(
            session
        )

        return self._set_question(
            session,
            question,
            question_type="primary",
        )

    def _set_question(
        self,
        session,
        question: str,
        question_type: str = "primary",
    ) -> dict[str, Any]:
        """Store the generated question in session state."""

        session.current_question = question

        session.current_question_day = (
            session.interview_plan
            .questions[
                session.current_question_index
            ]
            .day
        )

        session.current_question_type = (
            question_type
        )

        self.sessions.add_message(
            session.session_id,
            "assistant",
            question,
        )

        return {
            "reply": question,
            "done": False,
        }