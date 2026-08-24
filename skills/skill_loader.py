from pathlib import Path


class SkillLoader:
    """
    Load only explicitly allowed project skills.
    """

    def __init__(
        self,
        skills_directory: Path | None = None,
    ):

        self._skills_directory = (
            skills_directory
            or Path(__file__).resolve().parent
        )

        self._skill_paths = {
            "option-analysis": (
                self._skills_directory
                / "options"
                / "SKILL.md"
            ),
        }

    def load(
        self,
        skill_name: str,
    ) -> str:
        """
        Return the requested skill instructions as text.
        """

        skill_path = self._skill_paths.get(
            skill_name
        )

        if skill_path is None:
            raise ValueError(
                f"Unsupported skill: {skill_name}"
            )

        if not skill_path.is_file():
            raise FileNotFoundError(
                f"Skill file not found: {skill_path}"
            )

        content = skill_path.read_text(
            encoding="utf-8"
        ).strip()

        if not content:
            raise ValueError(
                f"Skill file is empty: {skill_path}"
            )

        return content