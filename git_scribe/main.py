import typer
from .commands import init, commit, pr

app = typer.Typer(
    name="git-scribe",
    help="A CLI tool to generate commit messages and pull requests using LLM.",
    add_completion=False,
)

app.command(name="init")(init.init)
app.command(name="commit", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})(commit.commit)
app.command(name="pr")(pr.pr)

if __name__ == "__main__":
    app()
