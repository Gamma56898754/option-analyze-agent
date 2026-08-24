from skills.skill_loader import SkillLoader


def test_load_option_analysis_skill():

    loader = SkillLoader()

    content = loader.load(
        "option-analysis"
    )

    assert "Option Analysis Skill" in content
    assert "run_option_analysis" in content

    try:
        loader.load("unsupported-skill")

    except ValueError:
        pass

    else:
        raise AssertionError(
            "Unsupported skill should raise ValueError"
        )

    print("SkillLoader test passed.")


if __name__ == "__main__":
    test_load_option_analysis_skill()