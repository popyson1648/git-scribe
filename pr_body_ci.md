### Summary
This PR introduces a robust CI/CD pipeline using GitHub Actions and local pre-commit hooks to ensure code quality, consistency, and automated testing.

### Background
To maintain a high-quality and stable codebase, especially as the project grows, it's crucial to automate code checks and testing. This prevents regressions, enforces a consistent code style, and makes the development process more reliable for all contributors.

### Changes
-   **GitHub Actions Workflow (`.github/workflows/ci.yml`)**:
    -   A new CI pipeline is configured to run on every push and pull request to the `main` branch.
    -   It automatically runs tests against multiple Python versions (3.8 to 3.12).
    -   It performs linting and format checks using `ruff`.
-   **Pre-commit Hooks (`.pre-commit-config.yaml`)**:
    -   Configured `pre-commit` to run `ruff` for linting and formatting automatically before each commit.
    -   Includes standard hooks for fixing trailing whitespace, end-of-file issues, and checking YAML files.
-   **Dependencies (`pyproject.toml`)**:
    -   Added `pre-commit` to the development dependencies.
