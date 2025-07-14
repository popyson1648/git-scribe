import pytest
from unittest.mock import MagicMock
from git_scribe.core import github

@pytest.fixture
def mock_requests(mocker):
    """Fixture to mock both requests.get and requests.post."""
    get = mocker.patch('requests.get')
    post = mocker.patch('requests.post')
    return get, post

def test_create_pull_request(mock_requests):
    """
    Tests that create_pull_request sends the correct payload to the GitHub API.
    """
    _, mock_post = mock_requests
    
    github.create_pull_request(
        token="test_token",
        owner="test_owner",
        repo_name="test_repo",
        title="Test PR",
        body="This is a test.",
        head="feature",
        base="main",
        draft=True,
        reviewers=["user1"],
        assignees=["user2"],
        labels=["bug"],
        milestone=10
    )

    expected_url = "https://api.github.com/repos/test_owner/test_repo/pulls"
    expected_payload = {
        "title": "Test PR",
        "body": "This is a test.",
        "head": "feature",
        "base": "main",
        "draft": True,
        "reviewers": ["user1"],
        "assignees": ["user2"],
        "labels": ["bug"],
        "milestone": 10
    }

    mock_post.assert_called_once()
    call_args, call_kwargs = mock_post.call_args
    assert call_args[0] == expected_url
    assert "json" in call_kwargs
    assert call_kwargs["json"] == expected_payload
    assert call_kwargs["headers"]["Authorization"] == "token test_token"

def test_get_milestone_id(mock_requests):
    """
    Tests that get_milestone_id correctly finds a milestone by name.
    """
    mock_get, _ = mock_requests
    
    # Mock the API response
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"title": "v1.0", "number": 1},
        {"title": "v2.0", "number": 2}
    ]
    mock_get.return_value = mock_response

    # Test finding an existing milestone
    milestone_id = github.get_milestone_id("test_token", "owner", "repo", "v2.0")
    assert milestone_id == 2

    # Test not finding a milestone
    milestone_id_not_found = github.get_milestone_id("test_token", "owner", "repo", "v3.0")
    assert milestone_id_not_found is None
