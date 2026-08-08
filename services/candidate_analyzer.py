from dataclasses import dataclass
from typing import Any


@dataclass
class CandidateProfile:
    candidate_id: str
    name: str
    job_role: str
    years_experience: int
    education: str
    status: str

    passed_days: list[int]
    skipped_days: list[int]

    first_try_days: list[int]
    repeated_attempt_days: list[int]

    mission_attempts: dict[int, int]

    commit_days: int
    missions_completed: int
    missions_first_try: int


def analyze_candidate(candidate: dict[str, Any]) -> CandidateProfile:
    """
    Convert raw candidate data into a structured interview profile.
    """

    member = candidate.get("member", {})
    missions = candidate.get("missions", [])
    signals = candidate.get("signals", {})

    passed_days = []
    skipped_days = []
    first_try_days = []
    repeated_attempt_days = []
    mission_attempts = {}

    for mission in missions:
        day = mission.get("day")

        if day is None:
            continue

        if mission.get("passed") is True:
            passed_days.append(day)

        if mission.get("skipped") is True:
            skipped_days.append(day)

        attempts = mission.get("attempts")

        if isinstance(attempts, int):
            mission_attempts[day] = attempts

            if attempts == 1:
                first_try_days.append(day)

            elif attempts > 1:
                repeated_attempt_days.append(day)

    return CandidateProfile(
        candidate_id=member.get("id", ""),
        name=member.get("name", ""),
        job_role=member.get("jobRole", ""),
        years_experience=member.get("yearsExperience", 0),
        education=member.get("education", ""),
        status=member.get("status", ""),

        passed_days=passed_days,
        skipped_days=skipped_days,

        first_try_days=first_try_days,
        repeated_attempt_days=repeated_attempt_days,

        mission_attempts=mission_attempts,

        commit_days=signals.get("commitDays", 0),
        missions_completed=signals.get("missionsCompleted", 0),
        missions_first_try=signals.get("missionsFirstTry", 0),
    )