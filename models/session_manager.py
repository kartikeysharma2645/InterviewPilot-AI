from dataclasses import dataclass, field
from typing import Any


@dataclass
class InterviewSession:
    session_id: str
    candidate: dict[str, Any]
    candidate_profile: Any
    interview_plan: Any

    current_question_index: int = 0
    history: list[dict[str, Any]] = field(default_factory=list)
    evaluations: list[dict[str, Any]] = field(default_factory=list)

    difficulty: str = "intermediate"
    completed: bool = False


class SessionManager:
    """Stores and manages active interview sessions in memory."""

    def __init__(self):
        self._sessions: dict[str, InterviewSession] = {}

    def create_session(
        self,
        session_id: str,
        candidate: dict[str, Any],
        candidate_profile: Any,
        interview_plan: Any,
    ) -> InterviewSession:

        if session_id in self._sessions:
            raise ValueError(
                f"Session already exists: {session_id}"
            )

        session = InterviewSession(
            session_id=session_id,
            candidate=candidate,
            candidate_profile=candidate_profile,
            interview_plan=interview_plan,
        )

        self._sessions[session_id] = session

        return session

    def get_session(self, session_id: str) -> InterviewSession | None:
        """Return an existing session."""

        return self._sessions.get(session_id)

    def delete_session(self, session_id: str) -> None:
        """Remove a session."""

        self._sessions.pop(session_id, None)

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
    ) -> None:

        session = self.get_session(session_id)

        if session is None:
            raise ValueError(
                f"Session not found: {session_id}"
            )

        session.history.append({
            "role": role,
            "content": content,
        })

    def add_evaluation(
        self,
        session_id: str,
        evaluation: dict[str, Any],
    ) -> None:

        session = self.get_session(session_id)

        if session is None:
            raise ValueError(
                f"Session not found: {session_id}"
            )

        session.evaluations.append(evaluation)

    def advance_question(self, session_id: str) -> None:
        """Move the session to the next primary question."""

        session = self.get_session(session_id)

        if session is None:
            raise ValueError(
                f"Session not found: {session_id}"
            )

        session.current_question_index += 1

    def mark_completed(self, session_id: str) -> None:
        """Mark an interview as completed."""

        session = self.get_session(session_id)

        if session is None:
            raise ValueError(
                f"Session not found: {session_id}"
            )

        session.completed = True