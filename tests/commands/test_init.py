import pytest
from unittest.mock import patch
import typer
from git_scribe.commands import init
from git_scribe.core import config

def test_init_creates_files(mocker):
    """
    Tests that the init command creates all necessary config files.
    """
    # Mock the config path to use a temporary directory
    mock_config_dir = mocker.patch.object(config, 'CONFIG_DIR')
    mocker.patch.object(config, 'CONFIG_FILE')
    
    # Mock typer.confirm to automatically say "yes"
    mocker.patch('typer.confirm', return_value=True)
    
    # Mock the existence check to return False (as if files don't exist)
    mocker.patch.object(config, 'config_file_exists', return_value=False)
    
    # Mock the create function to check if it's called
    mock_create = mocker.patch.object(config, 'create_default_config_files')

    init.init()

    mock_create.assert_called_once()

def test_init_files_exist(mocker):
    """
    Tests that the init command prompts for overwrite if files exist.
    """
    # Mock the existence check to return True
    mocker.patch.object(config, 'config_file_exists', return_value=True)
    
    # Mock typer.confirm to simulate the user saying "no" to overwrite
    mock_confirm = mocker.patch('typer.confirm', return_value=False)
    
    # Mock the create function to ensure it's NOT called
    mock_create = mocker.patch.object(config, 'create_default_config_files')

    # We expect a typer.Exit when the user cancels
    with pytest.raises(typer.Exit):
        init.init()

    mock_confirm.assert_called_once()
    mock_create.assert_not_called()
