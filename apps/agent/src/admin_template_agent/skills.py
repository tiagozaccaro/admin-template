"""Skills loader.

Skills are markdown bundles (optionally with YAML frontmatter) that describe
specialized behaviors the agent can apply. This loader discovers skills from
a directory and returns their metadata + content.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)


@dataclass
class Skill:
    """A discovered skill bundle."""

    name: str
    path: str
    description: str = ""
    triggers: list[str] = field(default_factory=list)
    content: str = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "path": self.path,
            "description": self.description,
            "triggers": list(self.triggers),
        }


def _parse_frontmatter(raw: str) -> tuple[dict, str]:
    """Split a markdown file into (frontmatter, body)."""
    if not raw.startswith("---"):
        return {}, raw
    parts = raw.split("---", 2)
    if len(parts) < 3:
        return {}, raw
    try:
        meta = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return {}, raw
    if not isinstance(meta, dict):
        return {}, raw
    return meta, parts[2]


def load_skills(skills_dir: str = "skills") -> list[Skill]:
    """Load all skill bundles from the given directory."""
    base = Path(skills_dir)
    if not base.exists():
        return []
    skills: list[Skill] = []
    for path in sorted(base.glob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".md", ".markdown", ".yaml", ".yml"}:
            continue
        try:
            raw = path.read_text(encoding="utf-8")
        except OSError:
            logger.warning("Could not read skill file %s", path)
            continue
        meta, body = _parse_frontmatter(raw)
        skills.append(
            Skill(
                name=path.stem,
                path=str(path),
                description=str(meta.get("description", "")),
                triggers=list(meta.get("triggers", []) or []),
                content=body.strip() or raw,
            )
        )
    return skills


def load_skill_names(skills_dir: str = "skills") -> list[str]:
    """Return just the names of discovered skills."""
    return [s.name for s in load_skills(skills_dir)]


__all__ = ["Skill", "load_skill_names", "load_skills"]
