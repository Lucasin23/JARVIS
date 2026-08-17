"""
Git Tools Module — Git repository management.
Status, branch info, recent commits, and common Git operations.
"""

import os
import subprocess


def _run_git(args: list[str], cwd: str | None = None) -> tuple[bool, str]:
    """Run a git command and return (success, output)."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True, text=True, timeout=10, cwd=cwd
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, result.stderr.strip()
    except Exception as e:
        return False, str(e)


def _extract_path(text: str) -> str | None:
    """Extract a directory path from text."""
    for prefix in ["git status", "git branch", "git log", "git info",
                   "repository status", "repo status", "in "]:
        if prefix in text.lower():
            idx = text.lower().index(prefix) + len(prefix)
            path = text[idx:].strip()
            if path and path != "in":
                return path
    return None


def git_status(text: str) -> str:
    """Get git repository status."""
    # Check for path
    path = _extract_path(text)
    cwd = os.path.expanduser(path) if path else os.getcwd()

    success, output = _run_git(["status", "--short", "--branch"], cwd=cwd)
    if not success:
        return f"Not a git repository, sir. {output}"

    if not output:
        return "Working tree is clean. No changes detected, sir."

    # Get branch info
    branch_success, branch = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=cwd)

    lines = output.split("\n")
    staged = [l for l in lines if l.startswith("A") or l.startswith("M") or l.startswith("D") or l.startswith("R")]
    unstaged = [l for l in lines if l.startswith(" M") or l.startswith(" D") or l.startswith(" R")]
    untracked = [l for l in lines if l.startswith("??")]

    report = f"Git Status ({cwd}):\n"
    if branch_success:
        report += f"  Branch: {branch}\n"
    if staged:
        report += f"  Staged changes ({len(staged)}):\n"
        for s in staged:
            report += f"    {s}\n"
    if unstaged:
        report += f"  Unstaged changes ({len(unstaged)}):\n"
        for u in unstaged:
            report += f"    {u}\n"
    if untracked:
        report += f"  Untracked files ({len(untracked)}):\n"
        for u in untracked[:10]:
            report += f"    {u}\n"
        if len(untracked) > 10:
            report += f"    ... and {len(untracked) - 10} more\n"

    return report.strip()


def git_log(text: str, limit: int = 10) -> str:
    """Show recent git commits."""
    path = _extract_path(text)
    cwd = os.path.expanduser(path) if path else os.getcwd()

    success, output = _run_git(
        ["log", f"--max-count={limit}", "--oneline", "--graph", "--decorate"], cwd=cwd
    )
    if not success:
        return f"Not a git repository, sir. {output}"

    if not output:
        return "No commits yet, sir."

    return f"Recent commits:\n{output}"


def git_branches(text: str) -> str:
    """List all branches."""
    path = _extract_path(text)
    cwd = os.path.expanduser(path) if path else os.getcwd()

    success, output = _run_git(["branch", "-a"], cwd=cwd)
    if not success:
        return f"Not a git repository, sir. {output}"

    return f"Git branches:\n{output}"


def git_info(text: str) -> str:
    """Comprehensive git repo information."""
    path = _extract_path(text)
    cwd = os.path.expanduser(path) if path else os.getcwd()

    # Check if it's a git repo
    success, _ = _run_git(["rev-parse", "--git-dir"], cwd=cwd)
    if not success:
        return f"'{cwd}' is not a git repository, sir."

    # Gather info
    _, branch = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=cwd)
    _, remote = _run_git(["remote", "-v"], cwd=cwd)
    _, last_commit = _run_git(["log", "-1", "--format=%H %an %ar %s"], cwd=cwd)
    _, status = _run_git(["status", "--short"], cwd=cwd)
    _, total_commits = _run_git(["rev-list", "--count", "HEAD"], cwd=cwd)

    changes = len([l for l in status.split("\n") if l.strip()]) if status else 0

    report = f"Git Repository Info:\n"
    report += f"  Path: {cwd}\n"
    report += f"  Branch: {branch}\n"
    report += f"  Total commits: {total_commits}\n"
    report += f"  Last commit: {last_commit}\n"
    report += f"  Pending changes: {changes} file(s)\n"
    if remote:
        report += f"  Remotes:\n"
        for line in remote.split("\n"):
            if line.strip():
                report += f"    {line}\n"

    return report.strip()


def git_pull(text: str) -> str:
    """Pull latest changes from remote."""
    path = _extract_path(text)
    cwd = os.path.expanduser(path) if path else os.getcwd()

    success, output = _run_git(["pull"], cwd=cwd)
    if not success:
        return f"Git pull failed: {output}"
    return f"Pull complete:\n{output}" if output else "Already up to date, sir."


def git_push(text: str) -> str:
    """Push changes to remote."""
    path = _extract_path(text)
    cwd = os.path.expanduser(path) if path else os.getcwd()

    success, output = _run_git(["push"], cwd=cwd)
    if not success:
        return f"Git push failed: {output}"
    return f"Push complete:\n{output}" if output else "Everything is up to date, sir."


# ---------------------------------------------------------------------------
# Wrapper functions for command routing
# ---------------------------------------------------------------------------

def git_log_wrapper(text: str) -> str:
    return git_log(text)

def git_branches_wrapper(text: str) -> str:
    return git_branches(text)

def git_info_wrapper(text: str) -> str:
    return git_info(text)

def git_pull_wrapper(text: str) -> str:
    return git_pull(text)

def git_push_wrapper(text: str) -> str:
    return git_push(text)
