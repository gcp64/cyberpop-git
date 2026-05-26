"""
Cyberpop Git Manager Module
Provides utility functions to execute Git commands via subprocesses safely.
Handles repository checks, staging files, committing, pushing, and log retrieval.
"""

import subprocess
import shutil
from typing import Optional

class GitError(Exception):
    """Custom exception for Git related errors."""
    pass

def is_git_installed() -> bool:
    """Checks if Git is installed on the user's system."""
    return shutil.which("git") is not None

def run_git_cmd(args: list[str]) -> str:
    """Executes a Git command and returns the stripped output, raising GitError on failure."""
    if not is_git_installed():
        raise GitError("Git command-line utility is not installed or not found in system PATH.")
    
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="ignore"
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() or e.stdout.strip() or f"Process exited with code {e.returncode}"
        raise GitError(f"Git command failed: git {' '.join(args)}\nReason: {error_msg}")
    except Exception as e:
        raise GitError(f"Unexpected error running git {' '.join(args)}: {str(e)}")

def is_git_repository() -> bool:
    """Checks if the current working directory is inside a Git repository."""
    try:
        output = run_git_cmd(["rev-parse", "--is-inside-work-tree"])
        return output.lower() == "true"
    except GitError:
        return False

def get_active_branch() -> str:
    """Retrieves the name of the current active branch."""
    return run_git_cmd(["branch", "--show-current"])

def has_staged_files() -> bool:
    """Checks if there are any staged changes (cached changes ready for commit)."""
    # diff-index returns exit code 1 if there are differences, or 0 if not
    try:
        output = run_git_cmd(["diff", "--cached", "--name-only"])
        return len(output.strip()) > 0
    except GitError:
        return False

def get_staged_diff() -> str:
    """Retrieves the git diff of staged changes."""
    return run_git_cmd(["diff", "--cached", "--no-color"])

def stage_all_files():
    """Stages all modified, deleted, and untracked files in the current repository."""
    run_git_cmd(["add", "."])

def stage_modified_files():
    """Stages all modified and deleted tracked files in the current repository, ignoring untracked files."""
    run_git_cmd(["add", "-u"])

def commit(message: str):
    """Commits the staged changes with the provided commit message."""
    run_git_cmd(["commit", "-m", message])

def push(remote: str = "origin", branch: Optional[str] = None):
    """Pushes the local commits to the remote repository."""
    target_branch = branch or get_active_branch()
    if not target_branch:
        raise GitError("Could not determine current active branch. Make sure you are on a branch.")
    run_git_cmd(["push", remote, target_branch])

def get_user_email() -> str:
    """Gets the configured git user email."""
    try:
        return run_git_cmd(["config", "user.email"])
    except GitError:
        return ""

def get_today_commits() -> list[str]:
    """Retrieves commits made since midnight (00:00:00) today for the current user email."""
    email = get_user_email()
    args = ["log", "--since=00:00:00", "--pretty=format:%s (%h)"]
    if email:
        args.append(f"--author={email}")
    
    try:
        output = run_git_cmd(args)
        if not output.strip():
            return []
        return [line.strip() for line in output.split("\n") if line.strip()]
    except GitError:
        return []

def get_status_short() -> str:
    """Returns a short summary status of the repository files."""
    return run_git_cmd(["status", "--short"])

def get_user_name() -> str:
    """Gets the configured git user name."""
    try:
        return run_git_cmd(["config", "user.name"])
    except GitError:
        return ""

def run_git_fast_import(commits_input: str) -> str:
    """Feeds the generated fast-import protocol structure directly into git fast-import."""
    if not is_git_installed():
        raise GitError("Git is not found in system PATH.")
    try:
        process = subprocess.Popen(
            ["git", "fast-import", "--quiet"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate(input=commits_input.encode("utf-8"))
        if process.returncode != 0:
            raise GitError(f"fast-import failed: {stderr.decode('utf-8', errors='ignore') or stdout.decode('utf-8', errors='ignore')}")
        return stdout.decode('utf-8', errors='ignore').strip()
    except Exception as e:
        raise GitError(f"Unexpected error running fast-import: {str(e)}")

def git_reset_hard():
    """Forces local workspace index and HEAD to align with fast-imported commit changes."""
    run_git_cmd(["reset", "--hard", "HEAD"])
