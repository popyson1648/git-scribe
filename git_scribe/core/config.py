from pathlib import Path
import toml
from rich.console import Console
from rich.panel import Panel
import typer

# --- Constants ---
CONFIG_DIR = Path.home() / ".config" / "git-scribe"
CONFIG_FILE = CONFIG_DIR / "config.toml"
SYS_PROMPT_COMMIT_FILE = CONFIG_DIR / "system_prompt_commit.md"
USER_PROMPT_COMMIT_FILE = CONFIG_DIR / "user_prompt_commit.md"
SYS_PROMPT_PR_FILE = CONFIG_DIR / "system_prompt_pr.md"
USER_PROMPT_PR_FILE = CONFIG_DIR / "user_prompt_pr.md"

# --- Default File Contents ---
DEFAULT_CONFIG_CONTENT = f"""[api_keys]
gemini = "YOUR_GEMINI_API_KEY"
github = "YOUR_GITHUB_PERSONAL_ACCESS_TOKEN"

[editor]
# (Optional) Specify a path to your editor, e.g., "code --wait" or "vim"
command = ""

[prompt_paths]
# You can use absolute paths or paths with ~ (e.g., ~/my_prompts/custom_commit.md)
system_commit = "{SYS_PROMPT_COMMIT_FILE}"
user_commit = "{USER_PROMPT_COMMIT_FILE}"
system_pr = "{SYS_PROMPT_PR_FILE}"
user_pr = "{USER_PROMPT_PR_FILE}"
"""

DEFAULT_SYSTEM_PROMPT_COMMIT = """You are an expert at generating Git commit messages that follow the Conventional Commits specification.

**Instructions:**
1.  **Format**: Your entire response MUST be the raw text of the commit message. The format is `<type>(<scope>): <subject>`, followed by an optional body separated by a blank line.
2.  **Types**: Use one of the following types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`.
3.  **Subject**: Use the imperative mood (e.g., "add", not "added"). Do not capitalize the first letter or end with a period.
4.  **Body**: Use the body to explain the "what" and "why" of the change.
5.  **No Extra Text**: Do NOT include any other explanation, preamble, or markdown fencing like ```.
"""

DEFAULT_USER_PROMPT_COMMIT = ""

DEFAULT_SYSTEM_PROMPT_PR = """You are an expert at generating clear and concise Pull Request titles and bodies.

**Instructions:**
1.  **Output Format**: Your entire response MUST strictly follow this format:
    - The very first line is the pull request title.
    - All subsequent lines are the pull request body.
2.  **Content Structure**: The body MUST contain ONLY the following sections: `### Summary`, `### Background`, and `### Changes`. Do not add any other sections like `Test Plan`.
3.  **No Extra Text**: Do NOT include any other explanation, preamble, or markdown fencing like ```.
"""

DEFAULT_USER_PROMPT_PR = ""

console = Console()

# --- Core Functions ---
def config_file_exists():
    """Checks if the config file exists."""
    return CONFIG_FILE.is_file()

def load_config():
    """Loads the configuration or exits if it doesn't exist."""
    if not config_file_exists():
        console.print("[bold red]Configuration file not found. Please run 'git-scribe init'.[/bold red]")
        raise typer.Exit(1)
    return toml.load(CONFIG_FILE)

def create_default_config_files():
    """Creates the directory and all default configuration and prompt files."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write(DEFAULT_CONFIG_CONTENT)
    with open(SYS_PROMPT_COMMIT_FILE, "w", encoding="utf-8") as f:
        f.write(DEFAULT_SYSTEM_PROMPT_COMMIT)
    with open(USER_PROMPT_COMMIT_FILE, "w", encoding="utf-8") as f:
        f.write(DEFAULT_USER_PROMPT_COMMIT)
    with open(SYS_PROMPT_PR_FILE, "w", encoding="utf-8") as f:
        f.write(DEFAULT_SYSTEM_PROMPT_PR)
    with open(USER_PROMPT_PR_FILE, "w", encoding="utf-8") as f:
        f.write(DEFAULT_USER_PROMPT_PR)

    console.print(
        Panel(
            "[bold green]Default configuration and prompt files created successfully![/bold green]\n\n"
            f"All files were created in:\n[cyan]{CONFIG_DIR}[/cyan]\n\n"
            f"Please open [cyan]{CONFIG_FILE}[/cyan] and add your API keys to get started.",
            title="Success",
            border_style="green"
        )
    )