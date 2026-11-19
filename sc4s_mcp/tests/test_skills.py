import asyncio

import pytest
from fastmcp import Client
from fastmcp.skills import SkillsClientExtension
from mcp.shared.exceptions import MCPError

from app import REPO_ROOT
from server import mcp

SKILL_URI = "skill://create-parser/SKILL.md"
SKILL_DIR = REPO_ROOT / "skills" / "create-parser"


def test_list_skills():
    async def check():
        async with Client(mcp, extensions=[SkillsClientExtension()]) as client:
            skills = await client.list_skills()

        expected_names = {
            "create-parser",
            "manage-sc4s-parsers",
            "manage-sc4s-splunk-metadata",
            "sc4s-guided-configuration",
            "sc4s-send-syslog",
            "troubleshoot-sc4s",
        }
        actual_names = {skill.frontmatter.name for skill in skills}
        assert expected_names == actual_names

    asyncio.run(check())


def test_get_skill():
    async def check():
        async with Client(mcp, extensions=[SkillsClientExtension()]) as client:
            skill = await client.get_skill(SKILL_URI)
            contents = await client.read_resource(skill.uri)

        assert skill.uri == SKILL_URI
        assert skill.frontmatter.name == "create-parser"
        assert skill.frontmatter.description
        assert len(contents) == 1
        assert contents[0].text == (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

    asyncio.run(check())


def test_read_skill_resource():
    async def check():
        async with Client(mcp) as client:
            contents = await client.read_resource(SKILL_URI)

        assert len(contents) == 1
        assert contents[0].text == (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

    asyncio.run(check())


def test_read_additional_skill_file():
    async def check():
        guide_uri = "skill://create-parser/parser-guide.md"
        async with Client(mcp, extensions=[SkillsClientExtension()]) as client:
            skill = await client.get_skill(SKILL_URI)
            assert guide_uri in {resource.uri for resource in skill.resources}
            contents = await client.read_resource(guide_uri)

        assert len(contents) == 1
        assert contents[0].text == (SKILL_DIR / "parser-guide.md").read_text(
            encoding="utf-8"
        )

    asyncio.run(check())


@pytest.mark.parametrize(
    "uri",
    [
        "skill://unknown/SKILL.md",
        "skill://create-parser/parser-guide.md",
        "skill://create-parser/../SKILL.md",
    ],
)
def test_get_skill_rejects_incorrect_paths(uri):
    async def check():
        async with Client(mcp, extensions=[SkillsClientExtension()]) as client:
            with pytest.raises(MCPError):
                await client.get_skill(uri)

    asyncio.run(check())


@pytest.mark.parametrize(
    "uri",
    [
        "skill://create-parser/missing.md",
        "skill://create-parser/../../sc4s_mcp/auth.py",
        "skill://create-parser/%2e%2e/%2e%2e/sc4s_mcp/auth.py",
    ],
)
def test_read_skill_resource_rejects_incorrect_paths(uri):
    async def check():
        async with Client(mcp) as client:
            with pytest.raises(MCPError):
                await client.read_resource(uri)

    asyncio.run(check())
