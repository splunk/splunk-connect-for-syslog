from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_mcp_image_packages_bash_script_and_configurator_skill():
    dockerfile = (ROOT / "sc4s_mcp" / "Dockerfile").read_text()
    dockerignore = (ROOT / "sc4s_mcp" / "Dockerfile.dockerignore").read_text()

    assert "apk add --no-cache bash ca-certificates" in dockerfile
    assert (
        "COPY --chown=mcp:mcp configuration-tool.sh ./configuration-tool.sh"
        in dockerfile
    )
    assert ".agents/skills/sc4s-configurator/" in dockerfile
    assert "!configuration-tool.sh" in dockerignore
    assert "!.agents/skills/sc4s-configurator/" in dockerignore
