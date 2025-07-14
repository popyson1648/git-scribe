import typer
from rich.console import Console
from rich.panel import Panel
from pathlib import Path
from typing import List
from ..core import config, git_utils, llm, editor

console = Console()

def commit(ctx: typer.Context):
    """
    Generates a commit message for staged changes, accepting git commit options.
    
    All unknown options will be passed directly to the underlying 'git commit' command.
    """
    cfg = config.load_config()
    gemini_api_key = cfg.get("api_keys", {}).get("gemini", "")
    if "YOUR_GEMINI_API_KEY" in gemini_api_key or not gemini_api_key:
        console.print("[red]Error: Gemini API key not found or not set in config.toml[/red]")
        raise typer.Exit(1)

    repo = git_utils.get_repo()
    if not repo:
        console.print("[red]Error: Not a git repository.[/red]")
        raise typer.Exit(1)

    passthrough_args = ctx.args
    
    use_all = "--all" in passthrough_args or "-a" in passthrough_args
    use_amend = "--amend" in passthrough_args

    if use_all:
        diff = git_utils.get_all_diff(repo)
    else:
        diff = git_utils.get_staged_diff(repo)

    if not diff.strip() and not use_amend:
        console.print("[yellow]No changes to commit. Please stage your changes or use --all.[/yellow]")
        raise typer.Exit()

    try:
        prompt_paths = cfg['prompt_paths']
        system_prompt_path = Path(prompt_paths['system_commit']).expanduser()
        user_prompt_path = Path(prompt_paths['user_commit']).expanduser()

        with open(system_prompt_path, 'r', encoding='utf-8') as f:
            system_prompt = f.read()
        with open(user_prompt_path, 'r', encoding='utf-8') as f:
            user_prompt = f.read()
    except (KeyError, FileNotFoundError) as e:
        console.print(f"[red]Error loading prompt files: {e}[/red]")
        raise typer.Exit(1)

    final_user_prompt = f"{user_prompt}\n\n--- Git Diff ---\n{diff}"
    
    if use_amend:
        try:
            last_message = git_utils.get_last_commit_message(repo)
            final_user_prompt += f"\n\n--- Previous Commit Message (to amend) ---\n{last_message}"
            system_prompt += "\n\nYou are amending a previous commit. Refine the provided message based on the new diff."
        except Exception:
            console.print("[yellow]Could not find previous commit to amend. Proceeding without it.[/yellow]")

    console.print("[cyan]Generating commit message from LLM...[/cyan]")
    try:
        commit_msg = llm.generate_text(gemini_api_key, system_prompt, final_user_prompt)
    except Exception as e:
        console.print(f"[red]Failed to generate text from LLM: {e}[/red]")
        raise typer.Exit(1)

    while True:
        console.print(Panel(commit_msg, title="[bold green]Generated Commit Message[/bold green]", border_style="green", expand=False))
        action = typer.prompt("Adopt this message? (y/n/e) [e]dit", default="y").lower()

        if action == 'y':
            try:
                git_utils.commit(commit_msg, passthrough_args)
                console.print("[bold green]Successfully committed.[/bold green]")
            except Exception as e:
                console.print(f"[bold red]Failed to commit: {e}[/red]")
                raise typer.Exit(1)
            break
        elif action == 'e':
            editor_command = editor.get_editor(cfg)
            commit_msg = editor.edit_content(commit_msg, editor_command)
            console.print("[cyan]Content updated. Please review.[/cyan]")
        else:
            console.print("[yellow]Operation cancelled.[/yellow]")
            break