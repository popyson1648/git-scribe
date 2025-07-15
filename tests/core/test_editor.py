from git_scribe.core import editor
from unittest.mock import patch


def test_get_editor_priority():
    """
    Tests that get_editor respects the priority: config > git > env > default.
    """
    # 1. Test highest priority: config file
    mock_config = {"editor": {"command": "editor_from_config"}}
    assert editor.get_editor(mock_config) == "editor_from_config"

    # 2. Test second priority: git config
    #    (Simulate config file being empty)
    mock_config_empty = {"editor": {"command": ""}}
    with patch("subprocess.check_output", return_value="editor_from_git\n") as mock_git:
        assert editor.get_editor(mock_config_empty) == "editor_from_git"
        mock_git.assert_called_with(["git", "config", "core.editor"], text=True)

    # 3. Test third priority: environment variable
    #    (Simulate both config and git being unavailable)
    with patch("subprocess.check_output", side_effect=FileNotFoundError), patch.dict(
        "os.environ", {"EDITOR": "editor_from_env"}
    ):
        assert editor.get_editor(mock_config_empty) == "editor_from_env"

    # 4. Test lowest priority: default fallback
    #    (Simulate all sources being unavailable)
    with patch("subprocess.check_output", side_effect=FileNotFoundError), patch.dict(
        "os.environ", {}, clear=True
    ):
        assert editor.get_editor(mock_config_empty) == "vi"
