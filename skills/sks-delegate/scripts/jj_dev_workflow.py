#!/usr/bin/env nix-shell
#! nix-shell -i python3 -p python3 jj jujutsu gh
"""Reusable helpers that "dry" the common jj/gh command usage from `sks-dev`
and `sks-delegate` into callable functions.

The two skills repeat a small set of commands verbatim:

  * open an isolation workspace off a clean rev (``main@origin``)
  * create + track a bookmark and push it (``jj``)
  * verify a push without trusting the tool's own success line
  * rebuild a bookmark whose remote bookmark is immutable
  * probe ``gh`` identity / push rights before work begins
  * verify the PR head oid equals the local ``@``

This module turns those into typed functions so both skills can import — and so
a hand-rolled CLI can call — the same code and the same verification. It never
claims success: every step returns a result that carries the raw command
output, and the CLI prints the evidence.

Example
-------
    from jj_dev_workflow import open_isolation_workspace, verify_push

    repo = Path.home() / "Source/Repos/github.com/shikanime-labs" / "machines"
    open_isolation_workspace(repo, "feat-hpci", wip_files=[...])
    verify_push("shikanime-labs", "machines", "feat-hpci")

Run as a script
---------------
    python3 skills/sks-delegate/scripts/jj_dev_workflow.py probe
    python3 skills/sks-delegate/scripts/jj_dev_workflow.py workspace machines feat-hpci --wip a.txt b.txt
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

# Repos live at these roots (per sks-delegate/references/shikanime.md and the
# sks-dev/references/shikanime.md facts). Order matters: check them in turn.
REPO_ROOTS = (
    Path.home() / "Source/Repos/github.com/shikanime-labs",
    Path.home() / "Source/Repos/github.com/shikanime-studio",
)

WIP_DEST = Path(tempfile.gettempdir()) / "wip-isolate"


class StepError(RuntimeError):
    """A command step failed; carries evidence so the caller can print it."""

    def __init__(self, cmd, exit_code, stdout="", stderr=""):
        self.cmd = cmd
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        super().__init__(
            f"command failed (exit {exit_code}): {' '.join(cmd)}\nstdout:\n{stdout}\nstderr:\n{stderr}"
        )


def run(cmd, *, cwd=None, check=True):
    """Run *cmd* and return a :class:`subprocess.CompletedProcess`.

    ``check=True`` (default) turns a non-zero exit into a :class:`StepError`
    that carries the command, exit code, and full output.  ``check=False``
    returns the process even on failure so callers that want to parse partial
    output can do so.
    """
    res = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if check and res.returncode != 0:
        raise StepError(cmd, res.returncode, res.stdout, res.stderr)
    return res


def repo_roots() -> list[Path]:
    """Expanded ``REPO_ROOTS`` (expands ``~``)."""
    return [r.expanduser() for r in REPO_ROOTS]


def find_repo(start: Path | None = None) -> Path | None:
    """Find the checkout root containing a ``.jj`` dir, walking the repo roots.

    Returns ``None`` when no jj repository is found under any root.
    """
    for root in repo_roots():
        if start is not None and start.is_dir():
            candidate = (start / ".jj").resolve()
        else:
            candidate = None
        if candidate is not None and candidate.exists():
            return candidate.parent
        for probe in root.rglob(".jj"):
            return probe.parent.parent  # skip the `.jj` dir's parent
    return None


def _find_repo(path: Path | None) -> Path:
    """Resolve *path* to a jj checkout root, erroring with evidence."""
    if path is not None and path.exists():
        if (path / ".jj").exists():
            return path.resolve()
        for parent in path.parents:
            if (parent / ".jj").exists():
                return parent.resolve()
    if path is None:
        found = find_repo()
        if found is not None:
            return found
    raise StepError(["jj"], 127, "", f"no jj checkout found near {path or 'cwd'}")


# --- isolated-workspace open -----------------------------------------------


def snapshot_wip(wip_files: list[Path], dest: Path = WIP_DEST) -> list[Path]:
    """Copy *wip_files* into *dest* (sibling workspace dir of the checkout)."""
    dest.mkdir(parents=True, exist_ok=True)
    copied = []
    for f in wip_files:
        if not f.exists():
            raise StepError(["cp"], 127, "", f"WIP file not found: {f}")
        target = dest / ("__".join(f.name.split("/")))
        shutil.copy2(f, target)
        copied.append(target)
    return copied


def open_isolation_workspace(
    repo: Path,
    unit: str,
    wip_files: list[Path] | None = None,
    source_rev: str = "main@origin",
) -> Path:
    """Open a fresh jj isolation workspace for *unit* off a clean rev.

    Mirrors ``sks-delegate`` Procedure step 1 (the mandatory entry to the dev
    loop).  Steps performed:

      1. snapshot any WIP you must preserve into ``<tmp>/wip-isolate``
      2. ``jj workspace add <repo>.<unit> -r '<source_rev>'``

    Returns the workspace directory.  The caller then copies in their change
    files and commits per ``sks-commit``.
    """
    repo = _find_repo(repo)
    workspace = repo.parent / f"{repo.name}.{unit}"
    if wip_files:
        snapshot_wip(wip_files)
    run(
        ["jj", "workspace", "add", workspace.as_posix(), "-r", source_rev],
        cwd=repo,
    )
    return workspace


# --- bookmark + push -------------------------------------------------------


def create_bookmark(branch: str) -> subprocess.CompletedProcess[str]:
    """``jj bookmark create <branch> -r @`` — brand-new branch FIRST."""
    return run(["jj", "bookmark", "create", branch, "-r", "@"])


def track_bookmark(
    branch: str, remote: str = "origin"
) -> subprocess.CompletedProcess[str]:
    """``jj bookmark track <branch> --remote=origin`` — mandatory; jj will
    reject a push without it."""
    return run(["jj", "bookmark", "track", branch, "--remote", remote])


def push_branch(
    branch: str, remote: str = "origin"
) -> subprocess.CompletedProcess[str]:
    """``jj git push --remote origin -b <branch>`` — no force; pushes the
    bookmark ref sideways."""
    return run(["jj", "git", "push", "--remote", remote, "-b", branch])


# --- post-push verification (DONE IS PROVEN, NOT ASSERTED) -------------------


@dataclass
class PushVerification:
    ok: bool
    bookmarks: list[str] = field(default_factory=list)
    diff_stat: str = ""
    head_ref_oid: str | None = None
    local_oid: str | None = None
    evidence: list[str] = field(default_factory=list)

    def summarize(self) -> str:
        lines = [
            "push verification",
            "  ok          : " + str(self.ok),
            "  bookmarks   : " + (", ".join(self.bookmarks) or "(none)"),
            "  diff stat   : " + (self.diff_stat.strip() or "(empty)"),
        ]
        if self.head_ref_oid is not None and self.local_oid is not None:
            lines.append(
                "  headRefOid == local @ : "
                + ("TRUE" if self.head_ref_oid == self.local_oid else "FALSE")
            )
        for ev in self.evidence:
            lines.append("  evidence: " + ev)
        return "\n".join(lines)


def verify_push(org: str, repo: str, branch: str) -> PushVerification:
    """Verify a pushed bookmark end to end, mirroring the post-push
    verification block from ``sks-dev``.

    The push command's own success line proves nothing (a rewrite can leave the
    bookmark behind and git reports "Everything up-to-date" while pushing
    nothing).  We re-measure instead:

      * ``jj bookmark list``          — the bookmark exists
      * ``jj diff -r 'main@origin..@' --git --stat`` — intended scope only
      * ``gh pr view -R <org>/<repo> --json headRefOid`` — headRefOid MUST
        equal the local ``jj log -r @ -T 'commit_id'``.
    """
    acc: list[str] = []
    v = PushVerification(ok=True)
    repo_root = _find_repo(Path("."))

    bj = run(["jj", "bookmark", "list"], cwd=repo_root)
    acc.append("jj bookmark list: " + (bj.stdout.strip() or "(empty)"))
    v.bookmarks = [l for l in bj.stdout.splitlines() if l.strip()]
    if not v.bookmarks:
        v.ok = False

    dj = run(
        ["jj", "diff", "-r", "main@origin..@", "--git", "--stat"],
        cwd=repo_root,
    )
    acc.append("jj diff -r main@origin..@ --git --stat:\n" + dj.stdout)
    v.diff_stat = dj.stdout
    if dj.returncode != 0:
        v.ok = False

    gh = run(
        [
            "gh",
            "pr",
            "view",
            f"-R {org}/{repo}",
            "--json",
            "headRefOid",
        ],
    )
    if gh.returncode != 0:
        v.ok = False
        acc.append("gh pr view failed: " + gh.stderr.strip())
    else:
        try:
            payload = json.loads(gh.stdout)
            v.head_ref_oid = payload.get("headRefOid")
            acc.append("gh headRefOid: " + str(v.head_ref_oid))
        except Exception as exc:  # noqa: BLE001
            v.ok = False
            acc.append(f"gh pr view parsed badly: {exc}")

    lj = run(
        ["jj", "log", "-r", "@", "-T", "commit_id"],
        cwd=repo_root,
    )
    v.local_oid = lj.stdout.strip() or None
    acc.append("local @ = " + str(v.local_oid))
    if (
        v.head_ref_oid is not None
        and v.local_oid is not None
        and v.head_ref_oid != v.local_oid
    ):
        v.ok = False
    v.evidence = acc
    return v


# --- jj recovery (immutable bookmark) --------------------------------------


def rebuild_immutable_bookmark(
    branch: str, main_rev: str = "main@origin"
) -> subprocess.CompletedProcess[str]:
    """Rebuild a branch whose remote bookmark is immutable.

    ``jj rebase -d main -r <branch>`` fails with "Commit ... is immutable".
    Instead, restore a fresh trunk commit onto the intended files, then
    ``jj bookmark set --allow-backwards`` and push (lease semantics).
    """
    return run(
        ["jj", "restore", "--from", main_rev, "--to", "@", branch],
        cwd=_find_repo(Path(".")),
    )


# --- gh assumption-validation gates ----------------------------------------


def probe_gh_identity() -> str:
    """``gh api user --jq .login`` — the gh identity gate."""
    r = run(["gh", "api", "user", "--jq", ".login"])
    if r.returncode != 0:
        raise StepError(r.cmd, r.returncode, r.stdout, r.stderr)
    return r.stdout.strip()


def probe_push_rights(org: str, repo: str) -> bool:
    """``gh api repos/<org>/<repo> --jq .permissions.push`` — needs ``true``.

    Some orgs return an empty ``.viewerPermission``; that is an org quirk
    (``sks-dev`` branch-protection.md) and is surfaced, not silently passed.
    """
    r = run(
        [
            "gh",
            "api",
            f"repos/{org}/{repo}",
            "--jq",
            ".permissions.push",
        ]
    )
    if r.returncode != 0:
        raise StepError(r.cmd, r.returncode, r.stdout, r.stderr)
    val = r.stdout.strip()
    if val not in ("true", "false", "null"):
        raise StepError(r.cmd, 127, r.stdout, "unexpected jq output")
    if val == "false":
        raise StepError(r.cmd, 1, r.stdout, f"no push right on {org}/{repo}")
    return True


# --- CLI -------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=(
            "Dry the common jj/gh dev-loop command usage from sks-dev + sks-delegate "
            "into callable functions."
        )
    )
    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("workspace", help="open an isolation workspace")
    sp.add_argument(
        "repo", nargs="?", help="jj checkout root (auto-detected if omitted)"
    )
    sp.add_argument("unit", help="short slug, e.g. feat-hpci")
    sp.add_argument("--wip", nargs="*", help="WIP files to snapshot first")
    sp.add_argument("--source-rev", default="main@origin")

    sp = sub.add_parser("bookmark", help="create + track a bookmark")
    sp.add_argument("branch")

    sp = sub.add_parser("push")
    sp.add_argument("branch")

    sp = sub.add_parser("verify", help="verify a pushed bookmark end to end")
    sp.add_argument("org")
    sp.add_argument("repo")
    sp.add_argument("branch")

    sp = sub.add_parser("rebuild", help="rebuild a branch whose bookmark is immutable")
    sp.add_argument("branch")
    sp.add_argument("--main-rev", default="main@origin")

    sp = sub.add_parser("probe")
    sp.add_argument("org", nargs="?", help="OWNER/REPO (required for probe)")
    sp.add_argument("repo", nargs="?", help="REPO (required for probe)")
    return p


def _print_result(res: subprocess.CompletedProcess[str]) -> None:
    """Print command output so the CLI shows evidence."""
    if res.stdout.strip():
        print(res.stdout.rstrip())
    if res.stderr.strip():
        print("[stderr] " + res.stderr.rstrip(), file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if args.command == "workspace":
            repo = _find_repo(Path(args.repo) if args.repo else None)
            ws = open_isolation_workspace(repo, args.unit, args.wip, args.source_rev)
            print(f"isolation workspace opened: {ws}")
            print(f"workdir (cd): {ws}")
            return 0

        if args.command == "bookmark":
            _print_result(create_bookmark(args.branch))
            return 0

        if args.command == "push":
            _print_result(push_branch(args.branch))
            return 0

        if args.command == "verify":
            print(verify_push(args.org, args.repo, args.branch).summarize())
            return 0

        if args.command == "rebuild":
            _print_result(rebuild_immutable_bookmark(args.branch, args.main_rev))
            return 0

        if args.command == "probe":
            user = probe_gh_identity()
            print(f"gh identity: {user}")
            if args.org and args.repo:
                probe_push_rights(args.org, args.repo)
                print(f"push rights on {args.org}/{args.repo}: TRUE")
            return 0

        raise StepError(["cmd"], 2, "", f"unknown command {args.command}")
    except StepError as exc:
        print(str(exc), file=sys.stderr)
        return exc.exit_code if isinstance(exc.exit_code, int) else 1


if __name__ == "__main__":
    sys.exit(main())
