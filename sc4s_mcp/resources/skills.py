"""Publish bundled workflows through the MCP Skills extension (SEP-2640)."""

from fastmcp.server.providers.skills import SkillsDirectoryProvider
from fastmcp.skills.extension import SkillsExtension

from app import REPO_ROOT, mcp

skills = SkillsDirectoryProvider(
    REPO_ROOT / "skills",
    experimental_skills=True,
)
mcp.add_provider(skills)
mcp.add_extension(SkillsExtension(providers=[skills]))
