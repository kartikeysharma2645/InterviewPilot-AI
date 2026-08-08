import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def load_json(filename):
    """Load and return JSON data from the data directory."""

    file_path = DATA_DIR / filename

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    except FileNotFoundError:
        raise FileNotFoundError(
            f"Data file not found: {file_path}"
        )

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid JSON in {filename}: {error}"
        )


def load_curriculum():
    """Load the interview curriculum."""

    return load_json("curriculum.json")


def load_candidates():
    """Load candidate data."""

    return load_json("candidates.json")

def get_candidates():
    """Return the list of candidates."""

    data = load_candidates()
    return data["candidates"]


def get_candidate(candidate_id):
    """Return a candidate by ID."""

    candidates = get_candidates()

    for candidate in candidates:
        if candidate.get("member", {}).get("id") == candidate_id:
            return candidate

    return None


def get_curriculum_days():
    """Return all curriculum days."""

    data = load_curriculum()
    return data["days"]


def get_curriculum_day(day_number):
    """Return a curriculum day by day number."""

    days = get_curriculum_days()

    for day in days:
        if day.get("day") == day_number:
            return day

    return None