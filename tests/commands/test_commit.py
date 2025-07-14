import pytest
from unittest.mock import patch, MagicMock
import typer

# Import the function to be tested
from git_scribe.commands.commit import commit

# Mock the dependencies at the point of use
@pytest.fixture
def mock_config(mocker):
    mock = mocker.patch('git_scribe.commands.commit.config')
    # Configure the mock to return a dictionary structure, simulating the real config
    mock.load_config.return_value = {
        "api_keys": {"gemini": "DUMMY_KEY"},
        "prompt_paths": {
            "system_commit": "/fake/system.md",
            "user_commit": "/fake/user.md"
        }
    }
    return mock

@pytest.fixture
def mock_git_utils(mocker):
    return mocker.patch('git_scribe.commands.commit.git_utils')

@pytest.fixture
def mock_llm(mocker):
    # Configure the mock to return a string, which is what rich.Panel expects
    mock = mocker.patch('git_scribe.commands.commit.llm')
    mock.generate_text.return_value = "feat: a generated message"
    return mock

@pytest.fixture
def mock_editor(mocker):
    return mocker.patch('git_scribe.commands.commit.editor')

# Mock the built-in open function to prevent FileNotFoundError
@pytest.fixture
def mock_open(mocker):
    return mocker.patch("builtins.open", mocker.mock_open(read_data=""))

def test_commit_no_changes(mock_config, mock_git_utils, mock_open):
    """Tests that the command exits if there are no staged changes."""
    mock_git_utils.get_staged_diff.return_value = ""
    mock_ctx = MagicMock(args=[])
    
    with pytest.raises(typer.Exit):
        commit(mock_ctx)

    mock_git_utils.get_staged_diff.assert_called_once()

def test_commit_flow_yes(mock_config, mock_git_utils, mock_llm, mock_editor, mock_open):
    """Tests the main successful workflow where the user accepts the message."""
    mock_git_utils.get_staged_diff.return_value = "fake diff"
    mock_ctx = MagicMock(args=[])
    
    with patch('typer.prompt', return_value='y'):
        commit(mock_ctx)

    mock_llm.generate_text.assert_called_once()
    mock_git_utils.commit.assert_called_once_with("feat: a generated message", [])

def test_commit_flow_edit_then_yes(mock_config, mock_git_utils, mock_llm, mock_editor, mock_open):
    """Tests the workflow where the user edits the message first."""
    mock_git_utils.get_staged_diff.return_value = "fake diff"
    mock_editor.edit_content.return_value = "edited message"
    mock_ctx = MagicMock(args=[])
    
    with patch('typer.prompt', side_effect=['e', 'y']):
        commit(mock_ctx)

    mock_editor.edit_content.assert_called_once()
    mock_git_utils.commit.assert_called_once_with("edited message", [])

def test_commit_flow_no(mock_config, mock_git_utils, mock_llm, mock_editor, mock_open):
    """Tests the workflow where the user cancels the operation."""
    mock_git_utils.get_staged_diff.return_value = "fake diff"
    mock_ctx = MagicMock(args=[])

    with patch('typer.prompt', return_value='n'):
        commit(mock_ctx)

    mock_git_utils.commit.assert_not_called()

def test_commit_all_flag(mock_config, mock_git_utils, mock_llm, mock_open):
    """Tests that the --all flag uses the correct diff function."""
    mock_ctx = MagicMock(args=["--all"])
    mock_git_utils.get_all_diff.return_value = "fake all diff"
    
    with patch('typer.prompt', return_value='n'):
        commit(mock_ctx)

    mock_git_utils.get_all_diff.assert_called_once()
    mock_git_utils.get_staged_diff.assert_not_called()

def test_commit_amend_flag(mock_config, mock_git_utils, mock_llm, mock_open):
    """Tests that the --amend flag gets the last commit message."""
    mock_ctx = MagicMock(args=["--amend"])
    mock_git_utils.get_staged_diff.return_value = "fake amend diff"
    mock_git_utils.get_last_commit_message.return_value = "old message"

    with patch('typer.prompt', return_value='n'):
        commit(mock_ctx)

    mock_git_utils.get_last_commit_message.assert_called_once()
    call_args, _ = mock_llm.generate_text.call_args
    assert "old message" in call_args[2]
