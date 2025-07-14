import os
import subprocess
import tempfile

def get_editor(config: dict) -> str:
    """Determines the editor to use based on a priority list."""
    # 1. from config.toml
    if config.get("editor", {}).get("command"):
        return config["editor"]["command"]
    # 2. from git config
    try:
        git_editor = subprocess.check_output(["git", "config", "core.editor"], text=True).strip()
        if git_editor:
            return git_editor
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    # 3. from environment variable
    if "EDITOR" in os.environ:
        return os.environ["EDITOR"]
    # 4. fallback
    return "vi"

def edit_content(content: str, editor: str) -> str:
    """Opens the given content in the specified editor and returns the edited content."""
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".md", encoding='utf-8') as tmpfile:
        tmpfile.write(content)
        tmpfile.flush()
        tmpfile_path = tmpfile.name
    
    try:
        # Handle editors that have arguments (e.g., "code --wait")
        editor_parts = editor.split()
        subprocess.run(editor_parts + [tmpfile_path], check=True)
        with open(tmpfile_path, 'r', encoding='utf-8') as f:
            return f.read()
    finally:
        os.unlink(tmpfile_path)
