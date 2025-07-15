### Summary

This PR fixes a bug in the `pr` command where it would fail with a `422 Unprocessable Entity` error when called without the `--head` or `--base` options.

### Background

When a `typer.Option` with a `default=None` is not provided on the command line, Typer passes a special `OptionInfo` object to the function instead of `None`.

The previous logic did not account for this, causing it to misinterpret the `head` and `base` branch arguments. This led to an invalid payload being sent to the GitHub API, resulting in a `422` error. This was identified through a process of elimination and confirmed by adding a failing unit test that reproduced the exact error condition.

### Changes

-   Updated `git_scribe/commands/pr.py` to explicitly check if the `head` and `base` arguments are strings (`isinstance(arg, str)`) before using them.
-   If the arguments are not strings (i.e., they are the `OptionInfo` object), the logic now correctly falls back to using the active branch name for `head` and fetching the default branch from the API for `base`.
-   This fix was validated by a new unit test in `tests/commands/test_pr.py` that now passes.

### Notes

This change makes the `pr` command more robust and reliable, ensuring it behaves intuitively for the end-user when no options are specified. The TDD approach was crucial in pinpointing this subtle bug related to the CLI framework's behavior.
