import pytest
import toml
from pathlib import Path
from git_scribe.core import config
import typer

def test_create_and_load_default_config(tmp_path: Path, mocker):
    """
    Tests if the default config file can be created and then loaded correctly.
    """
    # Use a temporary directory for the config file to avoid side effects
    mocker.patch.object(config, 'CONFIG_DIR', tmp_path)
    config.CONFIG_FILE = tmp_path / "config.toml" # Important: update the global path
    # Also patch the prompt file paths to use the temp directory
    mocker.patch.object(config, 'SYS_PROMPT_COMMIT_FILE', tmp_path / "system_prompt_commit.md")
    mocker.patch.object(config, 'USER_PROMPT_COMMIT_FILE', tmp_path / "user_prompt_commit.md")
    mocker.patch.object(config, 'SYS_PROMPT_PR_FILE', tmp_path / "system_prompt_pr.md")
    mocker.patch.object(config, 'USER_PROMPT_PR_FILE', tmp_path / "user_prompt_pr.md")


    # 1. Create the default config
    config.create_default_config_files()

    # 2. Check if the main config file was created
    assert config.CONFIG_FILE.is_file()

    # 3. Load the created config and verify its contents
    loaded_cfg = config.load_config()
    
    assert "api_keys" in loaded_cfg
    assert loaded_cfg["api_keys"]["gemini"] == "YOUR_GEMINI_API_KEY"
    
    assert "editor" in loaded_cfg
    
    assert "prompt_paths" in loaded_cfg
    assert Path(loaded_cfg["prompt_paths"]["system_commit"]).name == "system_prompt_commit.md"

def test_load_config_not_found(mocker):
    """
    Tests that load_config raises typer.Exit when the config file does not exist.
    """
    # Ensure the config file does not exist in a temporary path
    mocker.patch.object(config, 'CONFIG_FILE', Path("/tmp/non_existent_dir/config.toml"))
    
    with pytest.raises(typer.Exit):
        config.load_config()
