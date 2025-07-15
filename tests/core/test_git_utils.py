import pytest
from unittest.mock import MagicMock, patch
from git_scribe.core import git_utils


@pytest.fixture
def mock_repo():
    """Fixture to create a mock GitPython Repo object."""
    repo = MagicMock()
    repo.remotes.origin.url = "https://github.com/test_owner/test_repo.git"
    repo.head.commit.message = "Initial commit"
    return repo


def test_get_repo_info_https(mock_repo):
    """Tests parsing of a standard HTTPS remote URL."""
    owner, repo_name = git_utils.get_repo_info(mock_repo)
    assert owner == "test_owner"
    assert repo_name == "test_repo"


def test_get_repo_info_ssh():
    """Tests parsing of a standard SSH remote URL."""
    repo = MagicMock()
    repo.remotes.origin.url = "git@github.com:test_owner/test_repo.git"
    owner, repo_name = git_utils.get_repo_info(repo)
    assert owner == "test_owner"
    assert repo_name == "test_repo"


def test_get_diffs(mock_repo):
    """Tests that diff functions call the correct git command."""
    git_utils.get_staged_diff(mock_repo)
    mock_repo.git.diff.assert_called_with(cached=True)

    git_utils.get_all_diff(mock_repo)
    mock_repo.git.diff.assert_called_with()  # No args

    git_utils.get_branch_diff(mock_repo, "main")
    mock_repo.git.diff.assert_called_with("main...")


def test_get_last_commit_message(mock_repo):
    """Tests retrieval of the last commit message."""
    message = git_utils.get_last_commit_message(mock_repo)
    assert message == "Initial commit"


@patch("subprocess.run")
@patch("os.unlink")
@patch("tempfile.NamedTemporaryFile")
def test_commit(mock_tempfile, mock_unlink, mock_subprocess, mock_repo):
    """Tests that the commit function calls git commit with the correct arguments."""
    # Setup mock for the temporary file
    mock_file = MagicMock()
    mock_file.name = "/tmp/test_commit_msg"
    mock_tempfile.return_value.__enter__.return_value = mock_file

    message = "Test commit message"
    passthrough_args = ["--no-verify", "--author='Test Author'"]

    git_utils.commit(message, passthrough_args)

    # Verify the temp file was written to
    mock_file.write.assert_called_with(message)

    # Verify the git command was constructed and called correctly
    expected_command = [
        "git",
        "commit",
        "-F",
        "/tmp/test_commit_msg",
    ] + passthrough_args
    mock_subprocess.assert_called_with(expected_command, check=True)

    # Verify the temp file was deleted
    mock_unlink.assert_called_with("/tmp/test_commit_msg")
