import typer
from rich.console import Console
from rich.panel import Panel
from pathlib import Path
from ..core import config, git_utils, llm, editor, github

console = Console()

from typing import List

def pr(
    base: str = typer.Option(None, "--base", "-B", help="The branch to merge into. Defaults to the repository's default branch."),
    head: str = typer.Option(None, "--head", "-H", help="The branch to be merged. Defaults to the current branch."),
    draft: bool = typer.Option(False, "--draft", "-d", help="Create the pull request as a draft."),
    reviewers: List[str] = typer.Option(None, "--reviewer", "-r", help="Request a review from a user or team. Can be specified multiple times."),
    assignees: List[str] = typer.Option(None, "--assignee", "-a", help="Assign a user to this pull request. Can be specified multiple times."),
    labels: List[str] = typer.Option(None, "--label", "-l", help="Add a label to this pull request. Can be specified multiple times."),
    milestone: str = typer.Option(None, "--milestone", "-m", help="Add this pull request to a milestone by name."),
    project: List[str] = typer.Option(None, "--project", "-p", help="Add this pull request to a project. (Not yet supported)"),
):
    """Creates a pull request on GitHub."""
    if project:
        console.print("[bold yellow]Warning: --project option is not yet supported by git-scribe.[/bold yellow]")

    cfg = config.load_config()
    gemini_api_key = cfg.get("api_keys", {}).get("gemini", "")
    github_token = cfg.get("api_keys", {}).get("github", "")

    if "YOUR_GEMINI_API_KEY" in gemini_api_key or not gemini_api_key or \
       "YOUR_GITHUB_PERSONAL_ACCESS_TOKEN" in github_token or not github_token:
        console.print("[red]Error: Gemini or GitHub API key not found or not set in config.toml[/red]")
        raise typer.Exit(1)

    repo = git_utils.get_repo()
    if not repo:
        console.print("[red]Error: Not a git repository.[/red]")
        raise typer.Exit(1)

    owner, repo_name = git_utils.get_repo_info(repo)
    if not owner or not repo_name:
        console.print("[red]Error: Could not determine GitHub repository owner and name from remote URL.[/red]")
        raise typer.Exit(1)

    # Determine head and base branches
    head_branch = head if head else repo.active_branch.name
    if not base:
        # Fetch default branch from GitHub API if not specified
        try:
            repo_info_url = f"https://api.github.com/repos/{owner}/{repo_name}"
            headers = {"Authorization": f"token {github_token}"}
            repo_info = requests.get(repo_info_url, headers=headers).json()
            base_branch = repo_info.get("default_branch", "main")
            console.print(f"[cyan]Base branch not specified, using repository default: '{base_branch}'[/cyan]")
        except Exception:
            base_branch = "main" # Fallback
            console.print(f"[yellow]Could not fetch default branch, falling back to 'main'. Please specify with --base if this is incorrect.[/yellow]")
    else:
        base_branch = base

    diff = git_utils.get_branch_diff(repo, base_branch)
    if not diff.strip():
        console.print(f"[yellow]No changes found between '{head_branch}' and '{base_branch}'.[/yellow]")
        raise typer.Exit()

    # ... (The rest of the prompt generation logic remains the same) ...
    try:
        prompt_paths = cfg['prompt_paths']
        system_prompt_path = Path(prompt_paths['system_pr']).expanduser()
        user_prompt_path = Path(prompt_paths['user_pr']).expanduser()

        with open(system_prompt_path, 'r', encoding='utf-8') as f:
            system_prompt = f.read()
        with open(user_prompt_path, 'r', encoding='utf-8') as f:
            user_prompt = f.read()
    except (KeyError, FileNotFoundError) as e:
        console.print(f"[red]Error loading prompt files: {e}[/red]")
        console.print("Please check the paths in your config.toml or run 'git-scribe init' again.")
        raise typer.Exit(1)

    final_user_prompt = f"{user_prompt}\n\n--- Git Diff ---\n{diff}"

    console.print("[cyan]Generating PR title and body from LLM...[/cyan]")
    try:
        content = llm.generate_text(gemini_api_key, system_prompt, final_user_prompt)
    except Exception as e:
        console.print(f"[red]Failed to generate text from LLM: {e}[/red]")
        raise typer.Exit(1)

    try:
        title, body = content.split('\n', 1)
    except ValueError:
        title = content
        body = ""
    
    pr_content = f"Title: {title}\n\n{body}"

    while True:
        console.print(Panel(pr_content, title="[bold green]Generated Pull Request[/bold green]", border_style="green", expand=False))
        action = typer.prompt("Create this PR on GitHub? (y/n/e) [e]dit", default="y").lower()

        if action == 'y':
            final_title = pr_content.split('\n', 1)[0].replace("Title:", "").strip()
            final_body = pr_content.split('\n\n', 1)[1] if '\n\n' in pr_content else ""
            
            milestone_id = None
            if milestone:
                try:
                    console.print(f"[cyan]Fetching ID for milestone '{milestone}'...[/cyan]")
                    milestone_id = github.get_milestone_id(github_token, owner, repo_name, milestone)
                    if not milestone_id:
                        console.print(f"[bold yellow]Warning: Milestone '{milestone}' not found. Proceeding without it.[/bold yellow]")
                except Exception as e:
                    console.print(f"[bold yellow]Warning: Could not fetch milestone ID: {e}. Proceeding without it.[/bold yellow]")

            try:
                # Handle both comma-separated strings and lists from multiple options
                def to_list(val):
                    if not val:
                        return []
                    # Typer passes a list if multiple options are given, but a string if one option with commas is given.
                    if isinstance(val, str):
                        return [v.strip() for v in val.split(',')]
                    if isinstance(val, (list, tuple)):
                        # If it's already a list, but might contain comma-separated strings
                        processed_list = []
                        for item in val:
                            processed_list.extend([v.strip() for v in item.split(',')])
                        return processed_list
                    return []

                reviewers_list = to_list(reviewers)
                assignees_list = to_list(assignees)
                labels_list = to_list(labels)

                pr_data = github.create_pull_request(
                    token=github_token, owner=owner, repo_name=repo_name,
                    title=final_title, body=final_body, head=head_branch, base=base_branch, draft=draft,
                    reviewers=reviewers_list,
                    assignees=assignees_list,
                    labels=labels_list,
                    milestone=milestone_id
                )
                pr_url = pr_data["html_url"]
                console.print(f"[bold green]Successfully created pull request:[/bold green] [link={pr_url}]{pr_url}[/link]")
            except Exception as e:
                console.print(f"[red]Failed to create pull request: {e}[/red]")
                raise typer.Exit(1)
            break
        elif action == 'e':
            editor_command = editor.get_editor(cfg)
            pr_content = editor.edit_content(pr_content, editor_command)
            console.print("[cyan]Content updated. Please review.[/cyan]")
        else:
            console.print("[yellow]Operation cancelled.[/yellow]")
            break
