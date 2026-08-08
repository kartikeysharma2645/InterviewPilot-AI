from dataclasses import dataclass


@dataclass
class InterviewQuestionPlan:
    question_number: int
    day: int
    title: str
    objectives: list[str]
    difficulty: str
    reason: str


@dataclass
class InterviewPlan:
    questions: list[InterviewQuestionPlan]

    @property
    def curriculum_days(self) -> list[int]:
        return list(dict.fromkeys(
            question.day for question in self.questions
        ))


class InterviewPlanner:
    """Builds a personalized interview roadmap."""

    MIN_QUESTIONS = 8
    MIN_CURRICULUM_DAYS = 4

    def __init__(self, curriculum_repository):
        self.curriculum = curriculum_repository

    def create_plan(self, candidate_profile):
        completed_days = candidate_profile.passed_days

        if len(completed_days) < self.MIN_CURRICULUM_DAYS:
            raise ValueError(
                "Candidate must have at least four completed curriculum days."
            )

        selected_days = self._select_days(candidate_profile)

        questions = []

        for index, day_number in enumerate(selected_days, start=1):
            day = self.curriculum.get_day(day_number)

            difficulty = self._get_difficulty(
                day_number,
                candidate_profile
            )

            reason = self._get_reason(
                day_number,
                candidate_profile
            )

            questions.append(
                InterviewQuestionPlan(
                    question_number=index,
                    day=day_number,
                    title=day["title"],
                    objectives=day["objectives"],
                    difficulty=difficulty,
                    reason=reason,
                )
            )

        return InterviewPlan(questions=questions)

    def _select_days(self, candidate_profile):
        """
        Select curriculum days based on candidate history.
        """

        passed_days = candidate_profile.passed_days

        repeated_days = set(
            candidate_profile.repeated_attempt_days
        )

        first_try_days = set(
            candidate_profile.first_try_days
        )

        selected = []

        # Prioritize topics requiring multiple attempts.
        for day in repeated_days:
            if day in passed_days and day not in selected:
                selected.append(day)

        # Then prioritize first-try topics for deeper probing.
        for day in first_try_days:
            if day in passed_days and day not in selected:
                selected.append(day)

        # Fill remaining slots.
        for day in passed_days:
            if day not in selected:
                selected.append(day)

        if len(selected) >= self.MIN_QUESTIONS:
            return selected[:self.MIN_QUESTIONS]

        # Reuse days for additional question slots.
        expanded = selected.copy()
        index = 0

        while len(expanded) < self.MIN_QUESTIONS:
            expanded.append(
                selected[index % len(selected)]
            )
            index += 1

        return expanded

    def _get_difficulty(self, day_number, candidate_profile):
        if day_number in candidate_profile.first_try_days:
            return "advanced"

        if day_number in candidate_profile.repeated_attempt_days:
            return "intermediate"

        return "intermediate"

    def _get_reason(self, day_number, candidate_profile):
        if day_number in candidate_profile.first_try_days:
            return (
                "Completed on the first attempt; "
                "probe deeper understanding."
            )

        if day_number in candidate_profile.repeated_attempt_days:
            return (
                "Required multiple attempts; "
                "probe conceptual understanding."
            )

        return "Completed curriculum topic."