import git

def get_repo() -> git.Repo:
    """Gets the current git repository."""
    try:
        return git.Repo(search_parent_directories=True)
    except git.InvalidGitRepositoryError:
        return None

import git
import os
import subprocess
import tempfile

def get_repo() -> git.Repo:
    """Gets the current git repository."""
    try:
        return git.Repo(search_parent_directories=True)
    except git.InvalidGitRepositoryError:
        return None

def get_staged_diff(repo: git.Repo) -> str:
    """Returns the staged diff."""
    return repo.git.diff(cached=True)

def get_all_diff(repo: git.Repo) -> str:
    """Returns the diff of all tracked files."""
    return repo.git.diff()

def get_last_commit_message(repo: git.Repo) -> str:
    """Returns the message of the last commit."""
    return repo.head.commit.message

def commit(message: str, commit_args: list[str]):
    """Performs the commit, passing through any extra arguments."""
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8') as tmpfile:
        tmpfile.write(message)
        tmpfile_path = tmpfile.name
    
    try:
        command = ['git', 'commit', '-F', tmpfile_path] + commit_args
        subprocess.run(command, check=True)
    finally:
        os.unlink(tmpfile_path)



def get_branch_diff(repo: git.Repo, base_branch: str) -> str:
    """Returns the diff between the current branch and the base branch."""
    return repo.git.diff(f"{base_branch}...")

def get_repo_info(repo: git.Repo) -> tuple[str, str]:
    """Extracts owner and repo name from the remote URL."""
    try:
        remote_url = repo.remotes.origin.url
        if remote_url.startswith("https"):
            parts = remote_url.split('/')
            owner = parts[-2]
            repo_name = parts[-1].replace('.git', '')
        elif remote_url.startswith("git@"):
            parts = remote_url.split(':')[1].split('/')
            owner = parts[0]
            repo_name = parts[1].replace('.git', '')
        else:
            return None, None
        return owner, repo_name
    except (AttributeError, IndexError):
         return None, None
