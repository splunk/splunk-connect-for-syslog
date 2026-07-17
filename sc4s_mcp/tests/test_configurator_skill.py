from pathlib import Path


SKILL = (
    Path(__file__).resolve().parents[2]
    / ".agents"
    / "skills"
    / "sc4s-configurator"
    / "SKILL.md"
)


def test_configurator_skill_exposes_natural_language_workflow():
    text = SKILL.read_text()

    for requirement in (
        "name: sc4s-configurator",
        "Use when",
        "configure SC4S",
        "`configure_sc4s`",
        "`configuration-tool.sh`",
        "merge or replace",
        "exact final payload",
        "explicit confirmation",
        "`get_job_status`",
    ):
        assert requirement in text
