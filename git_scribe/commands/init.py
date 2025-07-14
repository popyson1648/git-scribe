import typer
from rich.console import Console
from rich.panel import Panel
from ..core import config

console = Console()

def init():
    """
    Creates a default set of configuration and prompt files.
    """
    if config.config_file_exists():
        console.print(f"[yellow]Configuration file already exists at:[/yellow] [cyan]{config.CONFIG_FILE}[/cyan]")
        if typer.confirm("Do you want to overwrite it and all default prompt files?"):
            pass
        else:
            console.print("Operation cancelled.")
            raise typer.Exit()
    
    config.create_default_config_files()
