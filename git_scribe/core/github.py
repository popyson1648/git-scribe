import requests
import json

def get_milestone_id(token: str, owner: str, repo_name: str, milestone_name: str) -> int | None:
    """Finds the ID of a milestone by its name."""
    api_url = f"https://api.github.com/repos/{owner}/{repo_name}/milestones"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()
    for milestone in response.json():
        if milestone['title'] == milestone_name:
            return milestone['number']
    return None

def create_pull_request(token: str, owner: str, repo_name: str, title: str, body: str, head: str, base: str, draft: bool, reviewers: list, assignees: list, labels: list, milestone: int | None) -> dict:
    """Creates a pull request on GitHub."""
    api_url = f"https://api.github.com/repos/{owner}/{repo_name}/pulls"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = {
        "title": title,
        "body": body,
        "head": head,
        "base": base,
        "draft": draft,
    }
    if reviewers:
        data["reviewers"] = reviewers
    if assignees:
        data["assignees"] = assignees
    if labels:
        data["labels"] = labels
    if milestone:
        data["milestone"] = milestone

    response = requests.post(api_url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()
