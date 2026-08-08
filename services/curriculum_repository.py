from typing import Any

from utils.json_loader import load_curriculum


class CurriculumRepository:
    """Provides access to the 31-day interview curriculum."""

    def __init__(self):
        self.curriculum = load_curriculum()
        self.days = self.curriculum.get("days", [])
        self.modules = self.curriculum.get("modules", [])

    def get_day(self, day_number: int) -> dict[str, Any] | None:
        """Return a curriculum day by its day number."""

        for day in self.days:
            if day.get("day") == day_number:
                return day

        return None

    def get_objectives(self, day_number: int) -> list[str]:
        """Return learning objectives for a curriculum day."""

        day = self.get_day(day_number)

        if day is None:
            return []

        return day.get("objectives", [])

    def get_tools(self, day_number: int) -> list[str]:
        """Return tools associated with a curriculum day."""

        day = self.get_day(day_number)

        if day is None:
            return []

        return day.get("tools", [])

    def get_title(self, day_number: int) -> str | None:
        """Return the title of a curriculum day."""

        day = self.get_day(day_number)

        if day is None:
            return None

        return day.get("title")

    def get_type(self, day_number: int) -> str | None:
        """Return the curriculum day type."""

        day = self.get_day(day_number)

        if day is None:
            return None

        return day.get("type")

    def get_all_days(self) -> list[dict[str, Any]]:
        """Return all curriculum days."""

        return self.days

    def get_cohort(self) -> Any:
        """Return cohort information."""

        return self.curriculum.get("cohort")