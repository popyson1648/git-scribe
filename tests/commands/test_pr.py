import pytest
from unittest.mock import patch
import typer

# Import the function to be tested
from git_scribe.commands.pr import pr


# Mock the dependencies
@pytest.fixture
def mock_config(mocker):
    mock = mocker.patch("git_scribe.commands.pr.config")
    mock.load_config.return_value = {
        "api_keys": {"gemini": "DUMMY_KEY", "github": "DUMMY_TOKEN"},
        "prompt_paths": {
            "system_pr": "/fake/system_pr.md",
            "user_pr": "/fake/user_pr.md",
        },
    }
    return mock


@pytest.fixture
def mock_git_utils(mocker):
    mock = mocker.patch("git_scribe.commands.pr.git_utils")
    mock.get_repo_info.return_value = ("test_owner", "test_repo")
    mock.get_branch_diff.return_value = "fake pr diff"
    # Mock active_branch.name
    mock.get_repo.return_value.active_branch.name = "feature-branch"
    return mock


@pytest.fixture
def mock_llm(mocker):
    mock = mocker.patch("git_scribe.commands.pr.llm")
    mock.generate_text.return_value = "Test PR Title\nTest PR Body"
    return mock


@pytest.fixture
def mock_editor(mocker):
    return mocker.patch("git_scribe.commands.pr.editor")


@pytest.fixture
def mock_github(mocker):
    mock = mocker.patch("git_scribe.commands.pr.github")
    mock.create_pull_request.return_value = {"html_url": "http://example.com/pr/1"}
    return mock


@pytest.fixture
def mock_open(mocker):
    return mocker.patch("builtins.open", mocker.mock_open(read_data=""))


def test_pr_no_changes(mock_config, mock_git_utils, mock_open):
    """Tests that the command exits if there are no changes."""
    mock_git_utils.get_branch_diff.return_value = ""

    with pytest.raises(typer.Exit):
        pr()

    mock_git_utils.get_branch_diff.assert_called_once()


def test_pr_flow_yes(mock_config, mock_git_utils, mock_llm, mock_github, mock_open):
    """Tests the main successful PR creation workflow with multiple options."""
    with patch("typer.prompt", return_value="y"):
        # Simulate passing multiple options, which Typer turns into a list
        pr(base="main", reviewers=["user1", "user2"], labels=["bug", "enhancement"])

    mock_llm.generate_text.assert_called_once()
    mock_github.create_pull_request.assert_called_once()

    _, kwargs = mock_github.create_pull_request.call_args
    assert kwargs["title"] == "Test PR Title"
    assert kwargs["body"] == "Test PR Body"
    assert kwargs["reviewers"] == ["user1", "user2"]
    assert kwargs["labels"] == ["bug", "enhancement"]


def test_pr_flow_yes_comma_separated(
    mock_config, mock_git_utils, mock_llm, mock_github, mock_open
):
    """Tests the workflow with comma-separated string arguments."""
    with patch("typer.prompt", return_value="y"):
        # Simulate passing a single option with comma-separated values
        pr(base="main", reviewers="user1,user2", labels="bug,enhancement")

    _, kwargs = mock_github.create_pull_request.call_args
    assert kwargs["reviewers"] == ["user1", "user2"]
    assert kwargs["labels"] == ["bug", "enhancement"]


def test_pr_flow_milestone(
    mock_config, mock_git_utils, mock_llm, mock_github, mock_open
):
    """Tests that the milestone is correctly handled."""
    mock_github.get_milestone_id.return_value = 5

    with patch("typer.prompt", return_value="y"):
        pr(milestone="v1.0")

    mock_github.get_milestone_id.assert_called_once_with(
        "DUMMY_TOKEN", "test_owner", "test_repo", "v1.0"
    )
    _, kwargs = mock_github.create_pull_request.call_args
    assert kwargs["milestone"] == 5
