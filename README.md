# git-scribe

<p align="center">
  <img src="https://raw.githubusercontent.com/popyson1648/git-llm/main/logo.png" alt="git-scribe logo" width="200"/>
</p>

<p align="center">
  <strong>Your AI-powered git assistant for crafting perfect commits and pull requests.</strong>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#customization">Customization</a> •
  <a href="#contributing">Contributing</a>
</p>

---

`git-scribe` is a command-line tool that leverages Large Language Models (LLMs) to automatically generate high-quality, conventional commit messages and pull request descriptions. It acts as a smart wrapper around your daily `git` commands, streamlining your workflow and improving your commit history.

## Features

- **AI-Generated Commit Messages**: Automatically generates well-formatted commit messages from your staged changes.
- **AI-Generated Pull Requests**: Creates detailed pull request titles and bodies from your branch diffs.
- **Full `git commit` Compatibility**: Supports passthrough of common `git commit` options like `--all` and `--amend`.
- **Full `gh pr create` Compatibility**: Supports common `gh pr create` options like `--reviewer`, `--label`, `--milestone`, and `--draft`.
- **Interactive Review & Edit**: Always prompts you to review and edit the AI-generated content before any action is taken.
- **Customizable Prompts**: Easily customize the AI's behavior by editing simple markdown files.

## Installation

### Prerequisites

- [Git](https://git-scm.com/)
- [Python 3.8+](https://www.python.org/)

### 1. Install `git-scribe`

You can install the tool directly from this GitHub repository:

```bash
pip install git+https://github.com/popyson1648/git-llm.git
```

*(Note: Once published to PyPI, this will become `pip install git-scribe`)*

### 2. Initial Setup

After installation, run the `init` command to create the necessary configuration files:

```bash
git-scribe init
```

This will create a new directory at `~/.config/git-scribe/`.

### 3. Configure API Keys

Open the newly created configuration file at `~/.config/git-scribe/config.toml` and add your API keys:

```toml
[api_keys]
gemini = "YOUR_GEMINI_API_KEY"
github = "YOUR_GITHUB_PERSONAL_ACCESS_TOKEN"
```

- **Gemini API Key**: Get yours from [Google AI Studio](https://aistudio.google.com/app/apikey).
- **GitHub Personal Access Token**: Create one [here](https://github.com/settings/tokens) with `repo` scope.

## Usage

### Creating a Commit

1.  Stage your files as you normally would (`git add .`).
2.  Run the `commit` command. `git-scribe` will generate a message for you to review.

```bash
git-scribe commit
```

You can also pass through `git commit` arguments:

```bash
# Commit all tracked files, not just staged ones
git-scribe commit --all

# Amend the previous commit
git-scribe commit --amend
```

### Creating a Pull Request

1.  Push your feature branch to the remote repository.
2.  Run the `pr` command.

```bash
# Create a PR against the 'main' branch
git-scribe pr --base main
```

Add reviewers, labels, and other attributes just like you would with `gh pr create`:

```bash
git-scribe pr --base main --reviewer <user> --label "bug,enhancement" --draft
```

## Command Reference

### `git-scribe commit [OPTIONS]`

Accepts most standard `git commit` options, including but not limited to:
- `--all`, `-a`
- `--amend`
- `--author=<author>`
- `--date=<date>`
- `--no-verify`

### `git-scribe pr [OPTIONS]`

Accepts the following options, compatible with `gh pr create`:
- `--base <branch>`, `-B <branch>`
- `--head <branch>`, `-H <branch>`
- `--reviewer <handle>`, `-r <handle>` (can be specified multiple times)
- `--assignee <login>`, `-a <login>` (can be specified multiple times)
- `--label <name>`, `-l <name>` (can be specified multiple times)
- `--milestone <name>`, `-m <name>`
- `--draft`, `-d`

## Customization

You can fully customize the AI's tone, language, and output format by editing the prompt files located in `~/.config/git-scribe/`.

- **System Prompts (`system_*.md`)**: These files instruct the AI on its role and the strict output format it must follow.
- **User Prompts (`user_*.md`)**: These files are for you. You can add your own project-specific guidelines, examples, or context to further guide the AI. They are empty by default and can be safely left that way.

## Contributing

Contributions are welcome! Please feel free to open an issue or submit a pull request.

### Development Setup

1.  Clone the repository.
2.  Create a virtual environment and activate it.
3.  Install the package in editable mode with development dependencies:
    ```bash
    pip install -e .[dev]
    ```
4.  Run tests:
    ```bash
    pytest
    ```

## License

This project is licensed under the [MIT License](LICENSE).
