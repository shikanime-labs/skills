from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
SKILLS_DIR = BASE / "skills"

_GC_DISCOVER = BASE / "skills" / "sks-gc" / "scripts" / "discover.py"

_NAME_RE = re.compile(r"^[A-Za-z0-9_-]+$")


def _frontmatter(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\s*$(.*?)^---\s*$", text, re.S)
    if not m:
        return {}
    try:
        import yaml
        return yaml.safe_load(m.group(1)) or {}
    except Exception:
        return {}


def register(ctx):
    _register_skills(ctx)
    ctx.register_hook("on_session_end", _on_session_end)


def _register_skills(ctx):
    if not SKILLS_DIR.is_dir():
        return
    for skill_dir in sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir()):
        md = skill_dir / "SKILL.md"
        if not md.is_file():
            continue
        name = skill_dir.name
        if not _NAME_RE.match(name):
            continue
        fm = _frontmatter(md)
        ctx.register_skill(name, md, fm.get("description") or "")


def _on_session_end(session_id, completed=True, interrupted=False, **_):
    if not _GC_DISCOVER.is_file():
        return "sks-gc: dry-run script not bundled."
    try:
        proc = subprocess.run(
            [sys.executable, str(_GC_DISCOVER)],
            capture_output=True, text=True, timeout=120,
        )
        out = (proc.stdout or "").strip()
        err = (proc.stderr or "").strip()
        if out:
            return out
        if err:
            return err
        return "sks-gc dry-run complete (nothing deleted)."
    except subprocess.TimeoutExpired:
        return "sks-gc dry-run timed out."
    except Exception as exc:  # fail open; never block the session
        return f"sks-gc dry-run error: {exc}"
